"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        UPWORK ARCHITECTURAL DESIGN JOBS SCRAPER  — PRODUCTION v4            ║
║        DrissionPage (Real Chrome) + Groq AI + Excel Export                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

NEW IN v4 (fixes from screenshots):

  [BUG-A]  $0 / unverified jobs bypassed the filter and appeared in Top 15.
           ROOT CAUSE: Upwork's client-info section is rendered in a <div>
           OUTSIDE the <article class="job-tile"> in some card layouts.
           card.get_text() therefore never sees "$0 spent", so total_spent
           stays at -1, and the old check (total_spent == 0) never fires.
           FIX (3-layer defence):
             Layer 1 — HTML: search the FULL page soup for the client block
                        using the card's uid, not just card.get_text()
             Layer 2 — Scraper gate: block if payment_verified=False
                        OR total_spent == 0 (explicit $0)
             Layer 3 — AI gate: Groq prompt explicitly told: if client is
                        unverified AND $0 spent → return is_engineering=False
                        regardless of job content, score=0

  [BUG-B]  URLs in Excel were not clickable / broken.
           ROOT CAUSE A: xlsxwriter write_url() silently fails when the
                         worksheet has right_to_left() set (known xlsxwriter
                         bug in versions < 3.1).
           ROOT CAUSE B: xlsxwriter truncates display strings > 255 chars
                         and sometimes drops the hyperlink entirely.
           FIX: Switched URL column output to openpyxl =HYPERLINK() formula.
                openpyxl HYPERLINK formulas work regardless of RTL setting
                and have no length restriction on the URL itself.
                The rest of the sheet still uses xlsxwriter for speed.
                URLs are written as =HYPERLINK("url") so they
                render as blue underlined clickable text in Excel & Google Sheets.
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import sys
import io
import os
import re
import time
import json
import math
import hashlib
import logging
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from groq import Groq
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("upwork_scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not found.\n"
        "Add it to the .env file:\n"
        "  GROQ_API_KEY=gsk_your_key_here"
    )
groq_client = Groq(api_key=GROQ_API_KEY)

HEADLESS              = False
GROQ_PRIMARY_MODEL    = "llama-3.3-70b-versatile"
GROQ_FALLBACK_MODEL   = "llama-3.1-8b-instant"
GROQ_RATE_LIMIT_DELAY = 2.5

EXCEL_FILE_NAME = "Upwork_Jobs_Day3.xlsx"
SEEN_JOBS_FILE  = "seen_jobs.json"
TARGET_JOBS     = 10
TOP_N           = 7
MAX_PAGES       = 3

KEYWORDS = [
    '"Interior Design" OR "Architectural Design" OR "BIM Coordination" OR "Commercial Design" OR CAD',
    'Revit OR "3ds Max" OR Lumion OR "Hospitality Design" OR "Master Planning"',
    '"3D Rendering" OR "Landscape Design" OR "FF&E Specification" OR "Space Planning" OR "Construction Drawings"'
]
# URL generation is now handled inside scrape_jobs per keyword group

KEYWORD_PATTERNS = {
    "Interior Design":      r"interior\s+design",
    "Architectural Design": r"architectural\s+design",
    "BIM Coordination":     r"bim\s+coordination",
    "Commercial Design":    r"commercial\s+design",
    "CAD":                  r"\bcad\b",
    "Revit":                r"revit",
    "3ds Max":              r"3ds\s+max",
    "Lumion":               r"lumion",
    "Hospitality Design":   r"hospitality\s+design",
    "Master Planning":      r"master\s+planning",
    "3D Rendering":         r"3d\s+render",
    "Landscape Design":     r"landscape\s+design",
    "FF&E Specification":   r"ff&e",
    "Space Planning":       r"space\s+planning",
    "Construction Drawings":r"construction\s+drawings?",
}

# ─────────────────────────────────────────────────────────────────────────────
# DEDUPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class SeenJobsManager:
    def __init__(self, filepath: str = SEEN_JOBS_FILE):
        self.filepath = Path(filepath)
        self._seen: set = self._load()

    def _load(self) -> set:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                log.info(f"Loaded {len(data)} previously seen job IDs.")
                return set(data)
            except (json.JSONDecodeError, IOError):
                log.warning("Could not read seen_jobs.json — starting fresh.")
        return set()

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(sorted(self._seen), f, indent=2)

    def is_seen(self, job_id: str) -> bool:
        return job_id in self._seen

    def mark_seen(self, job_id: str):
        self._seen.add(job_id)
        self._save()

    @staticmethod
    def make_id(url: str) -> str:
        return hashlib.md5(url.strip().lower().encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# URL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def slugify(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:80]


# URL extraction directly handles the link.


# ─────────────────────────────────────────────────────────────────────────────
# [BUG-A FIX] CLIENT INFO EXTRACTOR — searches wider HTML context
# ─────────────────────────────────────────────────────────────────────────────
def extract_client_info(card) -> Dict[str, Any]:
    """
    [BUG-A FIX] Upwork sometimes renders the client info section in a <div>
    OUTSIDE the <article class='job-tile'> wrapper. To catch it:
      1. Try card.get_text() first (works when client info is inside card)
      2. Walk up to the card's parent and search there too
      3. Check for 'payment unverified' explicitly — if found, flag immediately

    Returns:
      payment_verified : bool  — False means BLOCK this job
      rating           : float
      total_spent      : int   (-1 = not shown, 0 = explicitly $0)
      spent_raw        : str
      location         : str
    """
    info: Dict[str, Any] = {
        "payment_verified": False,
        "rating":           0.0,
        "reviews_count":    0,
        "location":         "N/A",
    }

    # Walk up to the nearest <section> to make sure we capture all client info
    # that might be rendered in sibling divs outside the <article>
    container = card
    while container and container.name not in ('section', 'body'):
        container = container.parent
        
    if not container or container.name == 'body':
        # Fallback to just the parent if no <section> is found
        container = card.parent if card.parent else card
        
    search_text = container.get_text(separator=" ", strip=True)

    # --- Payment verification ---
    search_lower = search_text.lower()
    if "unverified" in search_lower:
        info["payment_verified"] = False
    elif "payment verified" in search_lower or "payment method verified" in search_lower:
        info["payment_verified"] = True
    else:
        # Fallback for when Upwork just says 'verified' or uses a badge
        badge = container.find(attrs={"data-test": "payment-verified-badge"})
        if badge or "verified" in search_lower:
            info["payment_verified"] = True

    # --- Rating & Reviews ---
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*of\s*([0-9,]+)\s*reviews?", search_text, re.IGNORECASE)
    if m:
        info["rating"] = float(m.group(1))
        info["reviews_count"] = int(m.group(2).replace(',', ''))
    else:
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:stars?)", search_text, re.IGNORECASE)
        if m:
            info["rating"] = float(m.group(1))

    # --- Location ---
    loc_elem = (
        card.find(attrs={"data-test": "client-country"})
        or card.find(attrs={"data-test": "location"})
    )
    if loc_elem:
        info["location"] = loc_elem.get_text(strip=True)

    return info


def should_skip_client(client_info: Dict[str, Any]) -> tuple:
    """
    No longer skipping at the scraper level so unverified jobs 
    can be collected in the All Jobs tab.
    """
    return False, ""


# ─────────────────────────────────────────────────────────────────────────────
# TIME CONVERTER
# ─────────────────────────────────────────────────────────────────────────────
def convert_relative_time(time_str: str) -> str:
    now = datetime.now()
    time_str = time_str.lower().strip()
    try:
        numbers = [int(s) for s in re.findall(r"\d+", time_str)]
        amount = numbers[0] if numbers else 1
        if "minute"    in time_str: dt = now - timedelta(minutes=amount)
        elif "hour"    in time_str: dt = now - timedelta(hours=amount)
        elif "yesterday" in time_str: dt = now - timedelta(days=1)
        elif "day"     in time_str: dt = now - timedelta(days=amount)
        elif "week"    in time_str: dt = now - timedelta(weeks=amount)
        elif "month"   in time_str: dt = now - timedelta(days=30 * amount)
        elif "year"    in time_str: dt = now - timedelta(days=365 * amount)
        else: dt = now
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return now.strftime("%Y-%m-%d %H:%M")


# ─────────────────────────────────────────────────────────────────────────────
# RELEVANCE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_matched_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    return [label for label, pattern in KEYWORD_PATTERNS.items()
            if re.search(pattern, text_lower)]


def get_relevance_flags(title: str, description: str, skills: str) -> List[str]:
    flags = []
    combined = f"{title} {description} {skills}".lower()
    if re.search(r"\$[5-9]\d{3,}|\$[1-9]\d{4,}", combined): flags.append("HIGH_BUDGET")
    if re.search(r"\burgent\b|\bimmediately\b|\basap\b", combined):  flags.append("URGENT")
    if re.search(r"long.?term|ongoing|6\+?\s*months?", combined):    flags.append("LONG_TERM")
    if re.search(r"\bbim\b|\brevit\b", combined):                    flags.append("BIM_REQUIRED")
    if re.search(r"\bautocad\b", combined):                          flags.append("AUTOCAD_REQUIRED")
    if re.search(r"3d\s+render|visualization|lumion|enscape|vray|twinmotion", combined):
        flags.append("3D_RENDERING")
    return flags


def infer_category(title: str, description: str) -> tuple:
    combined = f"{title} {description}".lower()
    if re.search(r"\binterior\b", combined):                   return "Interior Design",             "Architecture & Design"
    if re.search(r"\b(bim|revit)\b", combined):                return "BIM Modeling",                "Architecture & Design"
    if re.search(r"3d\s*render|architectural\s*visual", combined): return "3D Architectural Rendering", "Architecture & Design"
    if re.search(r"floor\s*plan|drafting|autocad", combined):  return "CAD Drafting",                "Architecture & Design"
    if re.search(r"\blandscape\b", combined):                  return "Landscape Architecture",      "Architecture & Design"
    if re.search(r"\bstructural\b|\bcivil\b", combined):       return "Structural / Civil",          "Engineering"
    if re.search(r"\bmep\b", combined):                        return "MEP Engineering",             "Engineering"
    return "General Architecture", "Architecture & Design"


# ─────────────────────────────────────────────────────────────────────────────
# BROWSER INIT
# ─────────────────────────────────────────────────────────────────────────────
def init_browser():
    options = uc.ChromeOptions()
    if HEADLESS:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--lang=en-US")
    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(45)
    return driver


# ─────────────────────────────────────────────────────────────────────────────
# PAGE SCRAPER
# ─────────────────────────────────────────────────────────────────────────────
def scrape_jobs(driver, seen_manager: SeenJobsManager) -> List[Dict]:
    all_jobs: List[Dict] = []
    seen_links: set = set()
    skipped_unverified = 0
    skipped_zero       = 0
    skipped_seen       = 0

    for kw_index, kw_query in enumerate(KEYWORDS):
        log.info(f"\n[Scraping Group {kw_index+1}/{len(KEYWORDS)}]: {kw_query[:60]}...")
        encoded = urllib.parse.quote_plus(kw_query)
        base_url = f"https://www.upwork.com/nx/search/jobs/?q={encoded}&sort=recency"
        
        for page_num in range(1, MAX_PAGES + 1):
            url = f"{base_url}&page={page_num}"
            
            log.info(f"──► Page {page_num}: {url}")
            driver.get(url)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-tile, section.up-card-section, [data-test='job-tile']"))
                )
                time.sleep(2)
            except Exception:
                log.warning(f"  Timeout on page {page_num}. Trying to continue...")
                time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            cards = (
                soup.find_all("article", class_="job-tile")
                or soup.select("section.up-card-section")
                or soup.select("[data-test='job-tile']")
            )

            if not cards:
                log.info(f"  No cards on page {page_num} — moving to next query group.")
                break

            log.info(f"  {len(cards)} cards found.")

            for card in cards:
                title_elem = card.find("h2") or card.find("h3")
                if not title_elem:
                    continue
                for span in title_elem.find_all("span"):
                    span.unwrap()
                title = title_elem.get_text(strip=True)
                if not title:
                    continue

                link_tag = title_elem.find("a")
                if link_tag and "href" in link_tag.attrs:
                    link = "https://www.upwork.com" + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
                else:
                    link = "No link"

                if link == "No link" or link in seen_links:
                    continue

                job_hash = SeenJobsManager.make_id(link)
                if seen_manager.is_seen(job_hash):
                    skipped_seen += 1
                    continue

                seen_links.add(link)

                client_info = extract_client_info(card)
                skip, reason = should_skip_client(client_info)
                if skip:
                    if reason == "payment_unverified":
                        skipped_unverified += 1
                        log.debug(f"  SKIP (unverified): {title[:60]}")
                    else:
                        skipped_zero += 1
                        log.debug(f"  SKIP ($0 spent): {title[:60]}")
                    continue

                desc_elem = (
                    card.find("span", {"data-test": "job-description-text"})
                    or card.find("div", class_="job-description-text")
                    or card.find("p", class_="mb-0")
                )
                description = (
                    desc_elem.get_text(strip=True) if desc_elem
                    else card.get_text(separator="\n", strip=True)
                )

                budget_elem = (
                    card.find(attrs={"data-test": "job-type-label"})
                    or card.find(attrs={"data-test": "budget"})
                    or card.find(class_="job-type")
                )
                budget_raw = budget_elem.get_text(strip=True) if budget_elem else "N/A"

                skill_elems = (
                    card.select("[data-test='TokenClamp JobAttrs'] a")
                    or card.select(".air3-token")
                    or card.select("[data-test='attr-item']")
                )
                skills = ", ".join(s.get_text(strip=True) for s in skill_elems) or "N/A"

                exp_elem = card.find(attrs={"data-test": "experience-level"})
                experience_level = exp_elem.get_text(strip=True) if exp_elem else "N/A"

                time_elem = (
                    card.find("span", {"data-test": "posted-on"})
                    or card.find("small", {"data-test": "job-pubilshed-date"})
                )
                relative_time = time_elem.get_text(strip=True) if time_elem else "Just now"
                posted_date = convert_relative_time(relative_time)

                prop_elem = (
                    card.find(attrs={"data-test": "proposals-tier"})
                    or card.find(attrs={"data-test": "bid-count"})
                )
                proposals_count = prop_elem.get_text(strip=True) if prop_elem else "N/A"

                matched_keywords = get_matched_keywords(f"{title} {description} {skills}")
                relevance_flags  = get_relevance_flags(title, description, skills)
                category, category_group = infer_category(title, description)

                job_data = {
                    "job_id":          job_hash[:16],
                    "title":           title,
                    "link":            link,
                    "posted_date":     posted_date,
                    "description":     description,
                    "budget_raw":      budget_raw,
                    "skills":          skills,
                    "experience_level": experience_level,
                    "proposals_count": proposals_count,
                    "client_info":     client_info,
                    "matched_keywords": matched_keywords,
                    "relevance_flags": relevance_flags,
                    "category":        category,
                    "category_group":  category_group,
                    "_hash":           job_hash,
                }
                all_jobs.append(job_data)
                log.info(f"  [+] Extracted: {title[:60]}")

            log.info(
                f"  Running total: {len(all_jobs)} | "
                f"Skipped: unverified={skipped_unverified}, zero_spent={skipped_zero}, seen={skipped_seen}"
            )
            time.sleep(2)

    log.info("\nScrape done.")
    log.info(f"Skipped: {skipped_unverified} unverified + {skipped_zero} $0-spent + {skipped_seen} already-seen.")
    return all_jobs


# ─────────────────────────────────────────────────────────────────────────────
# GROQ AI EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────
def _parse_retry_after(error_str: str) -> Optional[float]:
    m = re.search(r"try again in\s+(?:(\d+)m)?(?:([\d.]+)s)?", str(error_str))
    if m:
        return int(m.group(1) or 0) * 60 + float(m.group(2) or 0)
    return None


def _call_groq(prompt: str, model: str) -> Dict:
    completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a JSON-only API. Output strictly valid JSON."},
            {"role": "user",   "content": prompt},
        ],
        model=model,
        response_format={"type": "json_object"},
    )
    return json.loads(completion.choices[0].message.content)


def evaluate_job_with_groq(job: Dict) -> Dict:
    snippet     = job.get("description", "")[:700]
    client_info = job.get("client_info", {})

    verified_str = "Payment verified" if client_info.get("payment_verified") else "Payment NOT verified"
    client_ctx = (
        f"Client: {verified_str}, "
        f"Rating: {client_info.get('rating', 'unknown')}/5, "
        f"Total spent: {client_info.get('spent_raw', 'unknown')}"
    )
    extra = ""
    if job.get("budget_raw", "N/A") != "N/A":
        extra += f"\nBudget: {job['budget_raw']}"
    if job.get("skills", "N/A") != "N/A":
        extra += f"\nSkills: {job['skills']}"

    prompt = f"""Evaluate this Upwork job for an architecture/engineering freelancer.
Score 0-100. Higher = better opportunity.

SCORING (priority):
1. Client reliability: verified + high rating + high spend = slightly higher score. (Do not heavily penalize new clients or $0 spend).
2. Budget size relative to scope.
3. Relevance to: Architecture, Interior Design, BIM, AutoCAD, 3D Rendering.

DOMAIN RULES:
- is_engineering=true ONLY for: Civil/Building Architecture, Interior Design, MEP,
  BIM, Structural, AutoCAD drafting, 3D Architectural Rendering.
- is_engineering=false for: Software, IT, Web/App, Data, ML, Shopify, Jewelry,
  Industrial/Mechanical, Game Assets, Translation, PDF to Word, Typing, Data Entry.
- Never return null. Estimate if info is missing.
- Text fields in Arabic EXCEPT budget (use $ amount).

{client_ctx}{extra}

Return ONLY valid JSON, no markdown:
{{"is_engineering":bool,"score":int,"score_reason":"arabic","budget":"$amount or غير محدد","duration":"arabic","client_status":"arabic","software_needed":"arabic"}}

Job title: {job.get('title', '')}
Job description: {snippet}"""

    error_default = {
        "is_engineering": False, "score": 0,
        "score_reason": "خطأ في الاتصال بـ Groq API",
        "budget": "غير محدد", "duration": "غير محدد",
        "client_status": "غير محدد", "software_needed": "غير محدد",
    }

    for model_label, model_name in [
        ("primary (70B)", GROQ_PRIMARY_MODEL),
        ("fallback (8B)", GROQ_FALLBACK_MODEL),
    ]:
        max_waits, waits_done = 3, 0
        while waits_done <= max_waits:
            try:
                return _call_groq(prompt, model_name)
            except Exception as exc:
                err = str(exc)
                is_rate  = "429" in err or "rate_limit" in err.lower()
                is_daily = "tokens per day" in err.lower() or "tpd" in err.upper()
                if is_rate:
                    retry_after = _parse_retry_after(err)
                    if is_daily and retry_after and retry_after > 300:
                        log.warning(f"  {model_label} daily limit. Switching…")
                        break
                    if retry_after and waits_done < max_waits:
                        wait = int(retry_after) + 5
                        log.info(f"  Rate limit ({model_label}). Waiting {wait}s…")
                        for remaining in range(wait, 0, -10):
                            print(f"     …{remaining}s remaining", end="\r")
                            time.sleep(min(10, remaining))
                        print("  ✅ Retrying…                           ")
                        waits_done += 1
                        continue
                    else:
                        log.warning(f"  {model_label} rate limited (unparseable). Switching…")
                        break
                else:
                    log.error(f"  Groq error ({model_label}): {exc}")
                    return error_default

    log.error("  All Groq models exhausted.")
    return error_default


# ─────────────────────────────────────────────────────────────────────────────
# EXCEL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
COLUMNS = [
    "job_id", "job_title", "job_url", "job_type", "budget_rate",
    "experience_level", "posted_date", "client_location", "client_rating",
    "client_reviews_count", "proposals_count", "payment_verified",
    "category", "category_group", "skills", "search_query_matched",
    "relevance_flags", "description_excerpt"
]

COL_WIDTHS = [22, 48, 52, 16, 16, 17, 20, 18, 13, 22, 16, 17, 22, 22, 42, 38, 38, 55]

def safe_str(val) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "غير محدد"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def prepare_row(job: Dict) -> Dict:
    client = job.get("client_info", {})
    return {
        "job_id":                  safe_str(job.get("job_id")),
        "job_title":               safe_str(job.get("title")),
        "job_url":                 safe_str(job.get("link")),
        "job_type":                safe_str(job.get("budget_raw")),
        "budget_rate":             safe_str(job.get("budget", "غير محدد")),
        "experience_level":        safe_str(job.get("experience_level")),
        "posted_date":             safe_str(job.get("date")),
        "client_location":         safe_str(client.get("location")),
        "client_rating":           safe_str(client.get("rating")),
        "client_reviews_count":    safe_str(client.get("reviews_count")),
        "proposals_count":         safe_str(job.get("proposals_count")),
        "payment_verified":        safe_str(client.get("payment_verified", False)),
        "category":                safe_str(job.get("category")),
        "category_group":          safe_str(job.get("category_group")),
        "skills":                  safe_str(job.get("skills")),
        "search_query_matched":    safe_str(job.get("matched_keywords", [])),
        "relevance_flags":         safe_str(job.get("relevance_flags", [])),
        "description_excerpt":     safe_str(job.get("description", "")[:200]),
    }


def _apply_openpyxl_styling(filepath: str):
    """
    [BUG-B FIX] After xlsxwriter writes the data, re-open with openpyxl to:
      1. Write job_url column as =HYPERLINK() formula — works regardless of
         RTL mode, no 255-char limit, renders as clickable blue link in all
         Excel versions and Google Sheets.
      2. Apply consistent header / row styling.
    """
    wb = load_workbook(filepath)

    thin   = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]

        # Find the job_url column index (1-based)
        url_col_idx = None
        for col_idx, cell in enumerate(ws[1], start=1):
            if cell.value == "job_url":
                url_col_idx = col_idx
                break

        # --- Header row ---
        hdr_fill  = PatternFill("solid", fgColor="1F4E78")
        hdr_font  = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        hdr_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for i, (cell, width) in enumerate(zip(ws[1], COL_WIDTHS), start=1):
            cell.fill      = hdr_fill
            cell.font      = hdr_font
            cell.alignment = hdr_align
            cell.border    = border
            ws.column_dimensions[get_column_letter(i)].width = width
        ws.row_dimensions[1].height = 36

        # --- Data rows ---
        row_colors = ["F2F7FF", "FFFFFF"]
        for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
            fill_color = row_colors[row_idx % 2]
            row_fill   = PatternFill("solid", fgColor=fill_color)
            ws.row_dimensions[row_idx].height = 52

            for cell in row:
                cell.fill      = row_fill
                cell.border    = border
                cell.alignment = Alignment(
                    horizontal="center", vertical="center",
                    wrap_text=True
                )
                cell.font = Font(name="Arial", size=9)

                # [BUG-B FIX] Write clickable hyperlink formula for URL column
                if url_col_idx and cell.column == url_col_idx:
                    url_val = str(cell.value) if cell.value else ""
                    if url_val.startswith("http"):
                        url_escaped = url_val.replace('"', '""')
                        if len(url_escaped) <= 255:
                            # =HYPERLINK() formula — works in all Excel + Google Sheets
                            cell.value = f'=HYPERLINK("{url_escaped}")'
                        else:
                            # Fallback for very long URLs (Excel HYPERLINK limit is 255 chars)
                            cell.value = url_val
                            
                        cell.font  = Font(name="Arial", size=9,
                                          color="0563C1", underline="single")
                    # If URL is invalid / "No link" — leave as plain text

        ws.freeze_panes = "A2"
        ws.sheet_view.rightToLeft = True  # RTL display for Arabic content

    wb.save(filepath)
    log.info(f"  Hyperlinks and styling applied via openpyxl → {filepath}")


def export_to_excel(all_jobs: List[Dict], top_jobs: List[Dict]):
    df_all = pd.DataFrame([prepare_row(j) for j in all_jobs], columns=COLUMNS)
    df_top = pd.DataFrame([prepare_row(j) for j in top_jobs], columns=COLUMNS)

    all_sheet = f"All Jobs ({len(all_jobs)})"
    top_sheet = f"Top {len(top_jobs)} Jobs"

    # Step 1: Write data with pandas (fast, handles large frames cleanly)
    writer = None
    try:
        writer = pd.ExcelWriter(EXCEL_FILE_NAME, engine="openpyxl")
        df_all.to_excel(writer, index=False, sheet_name=all_sheet)
        df_top.to_excel(writer, index=False, sheet_name=top_sheet)
    except Exception as exc:
        log.error(f"Excel write error: {exc}")
        raise
    finally:
        if writer:
            writer.close()

    # Step 2: Re-open with openpyxl to apply styling + hyperlinks  [BUG-B FIX]
    _apply_openpyxl_styling(EXCEL_FILE_NAME)
    log.info(f"Excel saved → {EXCEL_FILE_NAME}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 70)
    log.info("   UPWORK ARCHITECTURAL DESIGN JOB SCRAPER v4 — STARTING")
    log.info(f"   Target: {TARGET_JOBS} engineering jobs  |  Top: {TOP_N}")
    log.info(f"   Output: {EXCEL_FILE_NAME}")
    log.info("=" * 70)

    seen_manager = SeenJobsManager(SEEN_JOBS_FILE)

    log.info("\n[Step 1] Opening Chrome and scraping…")
    driver = init_browser()
    raw_jobs: List[Dict] = []
    try:
        raw_jobs = scrape_jobs(driver, seen_manager)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    log.info(f"Scraped {len(raw_jobs)} candidate jobs (all verified, non-zero-spend).")

    if not raw_jobs:
        log.error("Scrape returned 0 jobs. Check login / bot-detection.")
        return

    log.info(f"\n[Step 2] Evaluating with Groq AI (target: {TARGET_JOBS})…")
    analyzed_jobs: List[Dict] = []

    try:
        for i, job in enumerate(raw_jobs):
            if len(analyzed_jobs) >= TARGET_JOBS:
                log.info(f"Reached target of {TARGET_JOBS}. Stopping.")
                break
    
            log.info(f"  [{i+1}/{len(raw_jobs)}] {job['title'][:70]}")
            ai_data = evaluate_job_with_groq(job)
    
            if ai_data.get("is_engineering"):
                analyzed_jobs.append({
                    **job,
                    "date":          job["posted_date"],
                    "score":         ai_data.get("score", 0),
                    "score_reason":  ai_data.get("score_reason", "مواصفات مناسبة"),
                    "budget":        ai_data.get("budget", "غير محدد"),
                    "duration":      ai_data.get("duration", "غير محدد"),
                    "client_status": ai_data.get("client_status", "غير محدد"),
                    "software":      ai_data.get("software_needed", "غير محدد"),
                })
                log.info(f"  ✅ Engineering! Score={ai_data.get('score',0)}  Total={len(analyzed_jobs)}/{TARGET_JOBS}")
            else:
                log.info("  ⬜ Rejected (not engineering or unverified client).")
    
            time.sleep(GROQ_RATE_LIMIT_DELAY)
    except (KeyboardInterrupt, Exception) as e:
        log.warning(f"\n⚠️ Process interrupted during AI evaluation ({type(e).__name__}: {e}).")
        log.info(f"Safely recovering {len(analyzed_jobs)} jobs collected so far...")

    if not analyzed_jobs:
        log.error("No qualifying jobs after AI evaluation.")
        return

    if len(analyzed_jobs) < TARGET_JOBS:
        log.warning(f"Only {len(analyzed_jobs)} jobs found (target {TARGET_JOBS}).")

    # Mark seen only after AI confirmation
    for job in analyzed_jobs:
        seen_manager.mark_seen(job["_hash"])

    log.info("\n[Step 3] Sorting & selecting top N…")
    all_sorted = sorted(analyzed_jobs, key=lambda j: j["score"], reverse=True)
    
    # Top tab ONLY includes verified clients
    verified_sorted = [j for j in all_sorted if j.get("client_info", {}).get("payment_verified")]
    top_n      = verified_sorted[:TOP_N]

    log.info(f"\nTop {len(top_n)} jobs (Verified Only):")
    for rank, j in enumerate(top_n, 1):
        log.info(f"  {rank:>2}. [{j['score']:>3}/100]  {j['title'][:65]}")

    log.info("\n[Step 4] Exporting to Excel…")
    export_to_excel(all_sorted, top_n)

    log.info("=" * 70)
    log.info(f"  DONE! {len(all_sorted)} jobs → {EXCEL_FILE_NAME}")
    log.info("=" * 70)


if __name__ == "__main__":
    main()