"""
LinkedIn People Search scraper (Playwright, sync API).

Goal: collect exactly 50 profiles that match
  - Title:    "Sales Manager" OR "Sales Specialist" OR "Marketing Manager"
  - Location: Riyadh, Saudi Arabia OR Saudi Arabia
  - Keywords: "B2B" AND ("Training" OR "Employee Development" OR "Leadership Development")
and write them to B2B_Training_Sales_Riyadh.csv

Authentication (first match wins):
  1. Saved persistent browser session in ./.li_session (created on first run)
  2. LI_AT env var (value of your LinkedIn `li_at` cookie)
  3. LINKEDIN_EMAIL + LINKEDIN_PASSWORD env vars
  4. Manual login in the opened browser window (supports 2FA / captcha)

Usage:
  python linkedin_scraper.py --login-only    # one-time: sign in and save the session
  python linkedin_scraper.py                 # default: verify every profile (strict)
  python linkedin_scraper.py --no-verify     # trust LinkedIn's keyword match, skip profile visits
  python linkedin_scraper.py --target 50 --max-pages 15

Anti-restriction safeguards (all persist across runs, see --help "safety"):
  - daily caps: 70 profile views + 30 search pages per Riyadh day
  - random 2-5 min break every 15-20 page loads
  - runs only 09:00-18:00 Riyadh time, Sun-Thu
  - resumes exactly where it stopped (no page is loaded twice)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import BrowserContext, Page, TimeoutError as PWTimeout, sync_playwright

BASE_DIR = Path(__file__).resolve().parent
SESSION_DIR = BASE_DIR / ".li_session"
OUTPUT_CSV = BASE_DIR / "B2B_Training_Sales_Riyadh.csv"
STATE_FILE = BASE_DIR / ".scrape_state.json"
REJECTS_CSV = BASE_DIR / "rejected_candidates.csv"
USAGE_FILE = BASE_DIR / ".daily_usage.json"
RIYADH_TZ = timezone(timedelta(hours=3))  # Saudi Arabia: UTC+3, no DST

SAUDI_ARABIA_GEO = "100459316"  # LinkedIn geoUrn for Saudi Arabia (Riyadh is a subset)
LOGIN_TIMEOUT_SEC = 900  # overridable with --login-timeout (minutes)

TITLES = ["Sales Manager", "Sales Specialist", "Marketing Manager"]
KEYWORD_QUERY = 'B2B AND (Training OR "Employee Development" OR "Leadership Development")'

# Title matching (English + common Arabic equivalents)
TITLE_PATTERNS = [
    re.compile(r"\bsales\s+manager\b", re.I),
    re.compile(r"\bsales\s+specialist\b", re.I),
    re.compile(r"\bmarketing\s+manager\b", re.I),
    re.compile(r"مدير\s+(ال)?مبيعات"),
    re.compile(r"(أ|ا)خصائي\s+(ال)?مبيعات"),
    re.compile(r"مدير\s+(ال)?تسويق"),
]
LOCATION_PATTERN = re.compile(r"saudi|riyadh|\bksa\b|السعودية|الرياض", re.I)
B2B_PATTERN = re.compile(r"\bb2b\b|b-to-b|business[\s-]to[\s-]business", re.I)
TRAINING_PATTERN = re.compile(
    r"\btraining\b|employee\s+development|leadership\s+development|تدريب|تطوير\s+(الموظفين|القيادات|القيادة)",
    re.I,
)

CSV_COLUMNS = ["Full Name", "Current Job Title", "Current Company", "LinkedIn Profile URL", "Location"]

NOISE_LINE = re.compile(
    r"^(view .*profile|connect|message|follow|following|pending|send inmail|status is (online|offline|reachable)"
    r"|•.*|\d+(st|nd|rd|th)\+?|(1st|2nd|3rd\+?)( degree connection)?|.*degree connection|premium|verified"
    r"|عرض الملف الشخصي.*|تواصل|رسالة|متابعة)$",
    re.I,
)


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def human_pause(lo: float = 2.0, hi: float = 5.0) -> None:
    time.sleep(random.uniform(lo, hi))


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def normalize_url(url: str) -> str:
    url = url.split("?")[0].split("#")[0].rstrip("/")
    url = re.sub(r"^https?://([a-z]{2,3}\.)?linkedin\.com", "https://www.linkedin.com", url)
    return url + "/"


def matches_title(text: str) -> bool:
    return any(p.search(text or "") for p in TITLE_PATTERNS)


def split_title_company(text: str) -> tuple[str, str]:
    """'Sales Manager at ACME | B2B ...' -> ('Sales Manager', 'ACME')."""
    if not text:
        return "", ""
    text = re.sub(r"^(current|الحالي)\s*:\s*", "", text.strip(), flags=re.I)
    m = re.split(r"\s+(?:at|@|لدى|في)\s+|\s@", text, maxsplit=1)
    if len(m) == 2:
        title, company = m
        company = re.split(r"\s*[|•·,–—]\s*|\s+-\s+", company)[0]
        title = re.split(r"\s*[|•·]\s*", title)[-1]
        return title.strip(" -|"), company.strip(" -|")
    # no "at": take the segment that contains the job title
    for seg in re.split(r"\s*[|•·]\s*|\s+-\s+", text):
        if matches_title(seg):
            return seg.strip(), ""
    return text.split("|")[0].strip(), ""


def pick_title(text: str) -> str:
    """Return the exact matching title segment from a headline."""
    for seg in re.split(r"\s*[|•·,/]\s*|\s+-\s+|\s+(?:at|@)\s+", text or ""):
        if matches_title(seg):
            return seg.strip()
    return ""


def is_logged_in(page: Page) -> bool:
    url = page.url
    if any(k in url for k in ("/login", "/authwall", "/checkpoint", "/uas/", "signup")):
        return False
    try:
        return page.locator("input#session_key, input#username").count() == 0
    except Exception:
        return False


def wait_if_challenge(page: Page) -> None:
    """Pause while LinkedIn shows a checkpoint / captcha so the user can solve it."""
    while any(k in page.url for k in ("/checkpoint", "/captcha", "/authwall")):
        log("LinkedIn security checkpoint detected - solve it in the browser window (waiting)...")
        time.sleep(5)


# --------------------------------------------------------------------------------------
# auth
# --------------------------------------------------------------------------------------
def launch_context(pw, headless: bool) -> BrowserContext:
    kwargs = dict(
        user_data_dir=str(SESSION_DIR),
        headless=headless,
        viewport={"width": 1366, "height": 900},
        locale="en-US",
        args=["--disable-blink-features=AutomationControlled"],
    )
    try:
        return pw.chromium.launch_persistent_context(channel="chrome", **kwargs)
    except Exception:
        log("Installed Chrome not usable, falling back to Playwright Chromium.")
        return pw.chromium.launch_persistent_context(**kwargs)


def ensure_login(ctx: BrowserContext, page: Page) -> None:
    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    human_pause(2, 4)
    if is_logged_in(page):
        log("Using saved LinkedIn session.")
        return

    li_at = os.getenv("LI_AT")
    if li_at:
        log("Injecting li_at cookie from environment.")
        ctx.add_cookies([{
            "name": "li_at", "value": li_at, "domain": ".linkedin.com", "path": "/",
            "httpOnly": True, "secure": True, "sameSite": "None",
        }])
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        human_pause(2, 4)
        if is_logged_in(page):
            log("Logged in via li_at cookie.")
            return

    email, password = os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD")
    if email and password:
        log("Logging in with credentials from environment.")
        page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        page.fill("#username", email)
        human_pause(0.5, 1.5)
        page.fill("#password", password)
        human_pause(0.5, 1.5)
        page.click("button[type=submit]")
        page.wait_for_load_state("domcontentloaded")
        human_pause(3, 5)
        wait_if_challenge(page)
        if is_logged_in(page):
            log("Logged in with credentials.")
            return

    mins = LOGIN_TIMEOUT_SEC // 60
    log(f"Not logged in. Please log in manually in the opened browser window ({mins} min timeout)...")
    if "login" not in page.url:
        page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
    deadline = time.time() + LOGIN_TIMEOUT_SEC
    while time.time() < deadline:
        time.sleep(3)
        if "/feed" in page.url or ("linkedin.com" in page.url and is_logged_in(page) and "login" not in page.url):
            log("Manual login detected - session saved to .li_session for future runs.")
            return
    sys.exit(f"Login timed out after {mins} min. Re-run the script (or use --login-timeout) and log in.")


# --------------------------------------------------------------------------------------
# search results
# --------------------------------------------------------------------------------------
EXTRACT_CARDS_JS = r"""
() => {
  const root = document.querySelector('main') || document.body;
  const cards = new Map();
  for (const a of root.querySelectorAll('a[href*="/in/"]')) {
    if (a.closest('aside')) continue;
    const card = a.closest('[data-chameleon-result-urn]')
              || a.closest('[data-view-name="search-entity-result-universal-template"]')
              || a.closest('[role="listitem"]')
              || a.closest('li');
    if (!card || cards.has(card)) continue;           // first /in/ link in a card = the person
    cards.set(card, a);
  }
  const out = [];
  for (const [card, a] of cards) {
    const nameEl = a.querySelector('span[aria-hidden="true"]') || card.querySelector('span[dir="ltr"] span[aria-hidden="true"]');
    out.push({
      url: a.href,
      name: (nameEl ? nameEl.innerText : '').trim(),
      lines: card.innerText.split('\n').map(s => s.trim()).filter(Boolean),
    });
  }
  return out;
}
"""


def parse_card(raw: dict) -> dict | None:
    url = raw.get("url", "")
    if "/in/" not in url or "/search/results/people/headless" in url:
        return None
    lines = [l for l in raw["lines"] if not NOISE_LINE.match(l)]
    name = raw.get("name") or (lines[0] if lines else "")
    name = re.sub(r"\s+", " ", name).strip()
    if not name or name.lower().startswith("linkedin member") or name == "عضو LinkedIn":
        return None
    rest = [l for l in lines if l != name and not l.lower().startswith(("view ", "عرض"))]
    current = next((l for l in rest if re.match(r"^(current|الحالي)\s*:", l, re.I)), "")
    plain = [l for l in rest if not re.match(
        r"^(current|past|summary|skills|السابق|الحالي)\s*:|.*mutual connection|.*followers|.*متابع|^provides services", l, re.I)]
    headline = plain[0] if plain else ""
    location = plain[1] if len(plain) > 1 else ""
    return {"name": name, "url": normalize_url(url), "headline": headline,
            "location": location, "current": current}


def scroll_to_bottom(page: Page) -> None:
    last = 0
    for _ in range(12):
        page.mouse.wheel(0, random.randint(500, 900))
        time.sleep(random.uniform(0.4, 0.9))
        h = page.evaluate("document.body.scrollHeight")
        at_bottom = page.evaluate("window.innerHeight + window.scrollY >= document.body.scrollHeight - 50")
        if at_bottom and h == last:
            break
        last = h
    time.sleep(1)


def search_url(title: str | None, page_no: int, combined: bool = False) -> str:
    if combined:
        titles = " OR ".join(f'"{t}"' for t in TITLES)
        kw = f"{KEYWORD_QUERY} AND ({titles})"
        url = f"https://www.linkedin.com/search/results/people/?keywords={quote(kw)}"
    else:
        url = (f"https://www.linkedin.com/search/results/people/?keywords={quote(KEYWORD_QUERY)}"
               f"&titleFreeText={quote(title or '')}")
    url += f"&geoUrn={quote(json.dumps([SAUDI_ARABIA_GEO]))}&origin=FACETED_SEARCH"
    if page_no > 1:
        url += f"&page={page_no}"
    return url


def scrape_search_page(page: Page, url: str) -> list[dict]:
    page.goto(url, wait_until="domcontentloaded")
    wait_if_challenge(page)
    try:
        page.wait_for_selector('main a[href*="/in/"]', timeout=15000)
    except PWTimeout:
        if page.locator("text=/No results found/i").count():
            return []
        log("  results did not render in 15s (empty page or layout change).")
        return []
    human_pause(1.5, 3)
    scroll_to_bottom(page)
    cards = [parse_card(r) for r in page.evaluate(EXTRACT_CARDS_JS)]
    return [c for c in cards if c]


# --------------------------------------------------------------------------------------
# profile verification
# --------------------------------------------------------------------------------------
PROFILE_JS = r"""
() => {
  const main = document.querySelector('main') || document.body;
  const q = s => { const e = main.querySelector(s); return e ? e.innerText.trim() : ''; };
  let company = '';
  const btn = main.querySelector('button[aria-label^="Current company"], [aria-label^="Current company"]');
  if (btn) company = btn.getAttribute('aria-label').replace(/^Current company:\s*/i, '').replace(/\.\s*Click.*$/i, '').trim();
  return {
    name: q('h1'),
    headline: q('.text-body-medium.break-words') || q('div.text-body-medium'),
    location: q('span.text-body-small.inline.t-black--light.break-words') || q('.pv-text-details__left-panel span.text-body-small'),
    company,
    text: main.innerText,
  };
}
"""


def verify_profile(page: Page, cand: dict) -> tuple[bool, dict, str]:
    page.goto(cand["url"], wait_until="domcontentloaded")
    wait_if_challenge(page)
    try:
        page.wait_for_selector("main h1", timeout=15000)
    except PWTimeout:
        return False, cand, "profile did not load"
    human_pause(1.5, 3)
    scroll_to_bottom(page)  # lazy-loads About / Experience / Skills
    # expand truncated "…see more" texts (read-only action)
    for btn in page.locator("main button.inline-show-more-text__button, main button:has-text('see more')").all()[:8]:
        try:
            btn.click(timeout=1500)
        except Exception:
            pass
    data = page.evaluate(PROFILE_JS)
    text = data.get("text", "")

    merged = dict(cand)
    if data.get("name") and not data["name"].lower().startswith("linkedin member"):
        merged["name"] = data["name"]
    if data.get("headline"):
        merged["headline"] = data["headline"]
    if data.get("location"):
        merged["location"] = data["location"]
    if data.get("company"):
        merged["company"] = data["company"]

    if not B2B_PATTERN.search(text):
        return False, merged, "no B2B mention on profile"
    if not TRAINING_PATTERN.search(text):
        return False, merged, "no Training / Employee / Leadership Development mention"
    return True, merged, ""


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------
def build_row(c: dict) -> dict:
    cur_title, cur_company = split_title_company(c.get("current", ""))
    head_title, head_company = split_title_company(c.get("headline", ""))
    title = (pick_title(c.get("current", "")) and cur_title) or pick_title(c.get("headline", "")) or cur_title or head_title
    company = c.get("company") or cur_company or head_company
    return {
        "Full Name": c["name"],
        "Current Job Title": title,
        "Current Company": company,
        "LinkedIn Profile URL": c["url"],
        "Location": c.get("location", ""),
    }


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # BOM -> Excel shows Arabic correctly
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        w.writerows(rows)


class SafetyGuard:
    """Anti-restriction controls that persist across runs.

    - Daily caps on profile views and search pages (stored in .daily_usage.json, Riyadh calendar day)
    - A random 2-5 min break every 15-20 LinkedIn page loads
    - Only runs inside Riyadh working hours on Saudi workdays (Sun-Thu)
    """

    def __init__(self, args):
        self.args = args
        self.usage = json.loads(USAGE_FILE.read_text("utf-8")) if USAGE_FILE.exists() else {}
        self.actions_since_break = 0
        self.next_break_at = self._roll_break()

    # ---- time window -------------------------------------------------------------
    @staticmethod
    def now() -> datetime:
        return datetime.now(RIYADH_TZ)

    def outside_hours_reason(self) -> str | None:
        if self.args.ignore_hours:
            return None
        now = self.now()
        start, end = self.args.work_start, self.args.work_end
        # Python weekday(): Mon=0 ... Fri=4, Sat=5
        if now.weekday() in (4, 5) and not self.args.allow_weekend:
            return f"it's {now:%A} in Riyadh (Saudi weekend). Use --allow-weekend to override."
        if not (start <= now.hour < end):
            return f"Riyadh time is {now:%H:%M}, outside working hours {start:02d}:00-{end:02d}:00."
        return None

    # ---- daily caps --------------------------------------------------------------
    @property
    def today(self) -> dict:
        key = self.now().strftime("%Y-%m-%d")
        if key not in self.usage:
            self.usage[key] = {"profile_visits": 0, "search_pages": 0}
            for old in sorted(self.usage)[:-14]:  # keep two weeks of history
                del self.usage[old]
        return self.usage[key]

    def blocked(self, kind: str) -> str | None:
        """kind: 'profile' or 'search'. Returns a stop reason or None."""
        reason = self.outside_hours_reason()
        if reason:
            return reason
        t = self.today
        if kind == "profile" and t["profile_visits"] >= self.args.daily_profile_cap:
            return f"daily profile-view cap reached ({t['profile_visits']}/{self.args.daily_profile_cap})."
        if kind == "search" and t["search_pages"] >= self.args.daily_search_cap:
            return f"daily search-page cap reached ({t['search_pages']}/{self.args.daily_search_cap})."
        return None

    def record(self, kind: str) -> None:
        self.today["profile_visits" if kind == "profile" else "search_pages"] += 1
        USAGE_FILE.write_text(json.dumps(self.usage, indent=1), "utf-8")
        self.actions_since_break += 1
        if not self.args.no_breaks and self.actions_since_break >= self.next_break_at:
            secs = random.uniform(self.args.break_min * 60, self.args.break_max * 60)
            log(f"  Taking a {secs / 60:.1f}-min break (after {self.actions_since_break} page loads)...")
            time.sleep(secs)
            self.actions_since_break = 0
            self.next_break_at = self._roll_break()

    def _roll_break(self) -> int:
        return random.randint(self.args.break_every_min, self.args.break_every_max)

    def summary(self) -> str:
        t = self.today
        return (f"today: {t['profile_visits']}/{self.args.daily_profile_cap} profile views, "
                f"{t['search_pages']}/{self.args.daily_search_cap} search pages")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=50)
    ap.add_argument("--max-pages", type=int, default=20, help="max result pages per query")
    ap.add_argument("--max-profile-visits", type=int, default=160, help="safety cap on profile views per run")
    ap.add_argument("--no-verify", action="store_true", help="skip visiting profiles for keyword verification")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--login-timeout", type=int, default=15, help="minutes to wait for manual login")
    ap.add_argument("--login-only", action="store_true", help="just log in and save the session, then exit")
    # --- anti-restriction safeguards ---
    g = ap.add_argument_group("safety")
    g.add_argument("--daily-profile-cap", type=int, default=70, help="max profile views per Riyadh day (all runs)")
    g.add_argument("--daily-search-cap", type=int, default=30, help="max search result pages per Riyadh day (all runs)")
    g.add_argument("--break-every-min", type=int, default=15, help="take a break after N..")
    g.add_argument("--break-every-max", type=int, default=20, help="..to M page loads (random)")
    g.add_argument("--break-min", type=float, default=2, help="break length lower bound (minutes)")
    g.add_argument("--break-max", type=float, default=5, help="break length upper bound (minutes)")
    g.add_argument("--no-breaks", action="store_true")
    g.add_argument("--work-start", type=int, default=9, help="Riyadh hour to start (24h)")
    g.add_argument("--work-end", type=int, default=18, help="Riyadh hour to stop (24h)")
    g.add_argument("--allow-weekend", action="store_true", help="also run on Fri/Sat")
    g.add_argument("--ignore-hours", action="store_true", help="disable the working-hours window")
    args = ap.parse_args()
    global LOGIN_TIMEOUT_SEC
    LOGIN_TIMEOUT_SEC = args.login_timeout * 60

    guard = SafetyGuard(args)
    if not args.login_only:
        reason = guard.outside_hours_reason()
        if reason:
            sys.exit(f"Not starting: {reason}")
        log(f"Safety status - {guard.summary()}")

    state = json.loads(STATE_FILE.read_text("utf-8")) if STATE_FILE.exists() else {}
    accepted: list[dict] = state.get("accepted", [])
    seen: set[str] = set(state.get("seen", []))
    rejected: list[dict] = state.get("rejected", [])
    progress: dict[str, int] = state.get("progress", {})  # query label -> last fully processed page
    visits = 0
    stop_reason = ""

    def save_state():
        STATE_FILE.write_text(json.dumps({"accepted": accepted, "seen": sorted(seen), "rejected": rejected,
                                          "progress": progress}, ensure_ascii=False, indent=1), "utf-8")

    queries = [(t, False) for t in TITLES] + [(None, True)]

    with sync_playwright() as pw:
        ctx = launch_context(pw, args.headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        ensure_login(ctx, page)
        if args.login_only:
            log("Session saved. Run again without --login-only to scrape.")
            ctx.close()
            return

        for title, combined in queries:
            if len(accepted) >= args.target or stop_reason:
                break
            label = "combined boolean query" if combined else f'title="{title}"'
            if progress.get(label) == -1:
                log(f"=== Query {label}: already exhausted on a previous run, skipping.")
                continue
            start_page = progress.get(label, 0) + 1
            log(f"=== Query: {label} (starting at page {start_page})")
            for page_no in range(start_page, args.max_pages + 1):
                if len(accepted) >= args.target:
                    break
                if visits >= args.max_profile_visits:
                    stop_reason = f"per-run profile-visit cap reached ({visits})."
                    break
                stop_reason = guard.blocked("search") or ""
                if stop_reason:
                    break
                url = search_url(title, page_no, combined)
                log(f"Page {page_no}: {url}")
                cards = scrape_search_page(page, url)
                guard.record("search")
                if not cards:
                    log("  no more results for this query.")
                    progress[label] = -1  # exhausted
                    save_state()
                    break
                log(f"  {len(cards)} visible profiles on page")
                page_complete = True
                for c in cards:
                    if len(accepted) >= args.target:
                        break
                    if c["url"] in seen:
                        continue
                    if not (matches_title(c["headline"]) or matches_title(c["current"])):
                        seen.add(c["url"])
                        rejected.append({**c, "reason": "title mismatch"})
                        continue
                    if not LOCATION_PATTERN.search(c["location"]):
                        seen.add(c["url"])
                        rejected.append({**c, "reason": "location mismatch"})
                        continue
                    if args.no_verify:
                        ok, merged, reason = True, c, ""
                    else:
                        if visits >= args.max_profile_visits:
                            stop_reason = f"per-run profile-visit cap reached ({visits})."
                        else:
                            stop_reason = guard.blocked("profile") or ""
                        if stop_reason:
                            page_complete = False  # remaining cards stay unseen -> picked up next run
                            break
                        visits += 1
                        ok, merged, reason = verify_profile(page, c)
                        guard.record("profile")
                        human_pause(4, 9)
                    seen.add(c["url"])
                    if ok and not LOCATION_PATTERN.search(merged.get("location", "")):
                        ok, reason = False, "location mismatch (profile)"
                    if ok:
                        accepted.append(merged)
                        log(f"  [OK {len(accepted):>2}/{args.target}] {merged['name']} | {merged['headline'][:70]}")
                    else:
                        rejected.append({**merged, "reason": reason})
                        log(f"  [skip] {merged['name']} - {reason}")
                    save_state()
                if page_complete and len(accepted) < args.target:
                    progress[label] = page_no
                save_state()
                if stop_reason:
                    break
                human_pause(4, 8)  # between result pages
        ctx.close()

    rows = [build_row(c) for c in accepted[: args.target]]
    write_csv(rows, OUTPUT_CSV)
    with open(REJECTS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["name", "headline", "location", "current", "url", "company", "reason"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rejected)

    log(f"Done: {len(rows)} profiles -> {OUTPUT_CSV.name}  (rejected: {len(rejected)}, profile visits this run: {visits})")
    log(f"Safety status - {guard.summary()}")
    if stop_reason:
        log(f"Stopped early: {stop_reason}")
    if len(rows) < args.target:
        log("Fewer matches than target so far. Re-run later (e.g. tomorrow) - it resumes from .scrape_state.json.")


if __name__ == "__main__":
    main()
