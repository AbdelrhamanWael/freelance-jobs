"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     UPWORK ARCHITECTURAL DESIGN JOBS SCRAPER  — PRODUCTION v3               ║
║     Apify flash_mage/upwork Actor + Groq AI + Excel Export                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
    Uses the Apify `flash_mage/upwork` actor (4.59★, 99.5% success rate) to
    scrape Upwork job listings for architectural design roles. This actor uses:
      - In-house Upwork accounts  (no credential scraping)
      - Rotating residential proxies  (Apify-managed)
      - Built-in bot detection avoidance
    Then evaluates each job with Groq AI and exports to a formatted Excel file.

SEARCH CRITERIA (run as 6 separate queries for maximum coverage):
    - "Architectural Design" OR "Interior Design" OR "Floor Plan"
    - AutoCAD OR Revit OR BIM
    - "3D Rendering" OR "Architectural Visualization" OR "Exterior Rendering"

SETUP:
    1. Install dependencies:
       pip install apify-client groq python-dotenv pandas openpyxl xlsxwriter

    2. Add BOTH keys to the .env file in this folder:
       GROQ_API_KEY=gsk_your_key_here
       APIFY_API_TOKEN=apify_api_your_token_here

       Get your Apify token free at: https://console.apify.com/account/integrations
       (Free tier = $5/month credit — enough for many runs)

    3. Run:
       python upwork_scraper.py

OUTPUT:
    - Upwork_Architectural_Jobs.xlsx  (2 tabs: All Jobs + Top 15)
    - seen_jobs.json                  (deduplication memory)
    - upwork_scraper.log              (full run log)
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
from datetime import datetime, timedelta
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from groq import Groq
from apify_client import ApifyClient

# Fix Windows terminal encoding
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
# API KEYS & CLIENTS
# ─────────────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY not found.\n"
        "Add it to the .env file:\n  GROQ_API_KEY=gsk_your_key_here"
    )

groq_client = Groq(api_key=GROQ_API_KEY)
apify_client = ApifyClient(APIFY_API_TOKEN) if APIFY_API_TOKEN else None

# Apify proxy for residential IP rotation (bypasses Upwork bot detection)
APIFY_PROXY_URL = (
    f"http://groups-RESIDENTIAL,country-US:{APIFY_API_TOKEN}"
    f"@proxy.apify.com:8000"
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────


# ── Search URLs — passed as startUrls to the actor ───────────────────────────
# The flash_mage/upwork actor requires full Upwork search URLs via `startUrls`,
# NOT a plain keyword string. We build 6 targeted URLs covering all 3 criteria.
import urllib.parse as _up

def _build_url(q: str, sort: str = "recency") -> str:
    return "https://www.upwork.com/nx/search/jobs/?" + _up.urlencode({"q": q, "sort": sort})

SEARCH_URLS = [
    _build_url('Architectural Design AutoCAD "3D Rendering"'),
    _build_url('Interior Design AutoCAD "Architectural Visualization"'),
    _build_url('Revit BIM "Architectural Design"'),
    _build_url('3D Rendering "Exterior Rendering" architecture'),
    _build_url('Floor Plan AutoCAD BIM'),
    _build_url('Interior Design Revit "3D Rendering"'),
]

# ── Scraping targets ──────────────────────────────────────────────────────────
TARGET_JOBS     = 35    # minimum engineering jobs to collect (after AI filter)
TOP_N           = 15    # jobs for the curated Top tab in Excel
MAX_PER_QUERY   = 10    # max results per Apify actor run

# ── Groq models ───────────────────────────────────────────────────────────────
GROQ_PRIMARY_MODEL   = "llama-3.3-70b-versatile"   # 100K tokens/day free
GROQ_FALLBACK_MODEL  = "llama-3.1-8b-instant"       # 500K tokens/day free
GROQ_RATE_LIMIT_DELAY = 2.5                          # seconds between AI calls

# ── Output files ──────────────────────────────────────────────────────────────
EXCEL_FILE_NAME = "Upwork_Architectural_Jobs.xlsx"
SEEN_JOBS_FILE  = "seen_jobs.json"

# ─────────────────────────────────────────────────────────────────────────────
# DEDUPLICATION  (seen_jobs.json)
# ─────────────────────────────────────────────────────────────────────────────
class SeenJobsManager:
    """Persists scraped job URL hashes so subsequent runs skip old jobs."""

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
# URL NORMALISER
# ─────────────────────────────────────────────────────────────────────────────
def normalize_upwork_url(raw_url: str) -> str:
    """
    Ensure a job URL uses the canonical public /jobs/~TOKEN/ format.
    This format works without login.
    The /freelance-jobs/apply/ format requires login (shows 'We'll be back').
    """
    if not raw_url:
        return "No link"
    raw_url = raw_url.strip()

    # Already correct public format
    if re.search(r"upwork\.com/jobs/~", raw_url):
        return raw_url

    # Extract token from any Upwork URL pattern
    m = re.search(r"(~[0-9a-zA-Z]{16,})", raw_url)
    if m:
        return f"https://www.upwork.com/jobs/{m.group(1)}/"

    # Relative path
    if raw_url.startswith("/"):
        return f"https://www.upwork.com{raw_url}"

    if raw_url.startswith("http"):
        return raw_url

    return "No link"


# ─────────────────────────────────────────────────────────────────────────────
# UPWORK DIRECT SEARCH  (via Apify residential proxy)
# ─────────────────────────────────────────────────────────────────────────────

# Request headers that mimic a real browser visiting Upwork
_HEADERS = {
    "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept":           "application/json, text/plain, */*",
    "Accept-Language":  "en-US,en;q=0.9",
    "Referer":          "https://www.upwork.com/nx/search/jobs/",
    "X-Requested-With": "XMLHttpRequest",
    "Origin":           "https://www.upwork.com",
}

# Upwork's internal search API (same one the browser frontend calls)
_UPWORK_SEARCH = "https://www.upwork.com/search/jobs/url"


def _get_proxy() -> dict:
    """Return requests proxy dict using Apify residential proxy."""
    proxy_url = f"http://groups-RESIDENTIAL,country-US:{APIFY_API_TOKEN}@proxy.apify.com:8000"
    return {"http": proxy_url, "https": proxy_url}


def search_upwork(query: str, per_page: int = MAX_PER_QUERY, page: int = 1) -> list[dict]:
    """
    Call Upwork's search API directly through Apify residential proxy.
    Returns a list of raw job result dicts.
    """
    log.info(f"  [Search] Query: '{query[:60]}' page {page}…")

    params = {
        "q":       query,
        "sort":    "recency",
        "per_page": per_page,
        "page":    page,
    }

    try:
        resp = requests.get(
            _UPWORK_SEARCH,
            params=params,
            headers=_HEADERS,
            proxies=_get_proxy(),
            timeout=30,
            verify=False,   # Apify proxy uses its own cert
        )

        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "")
            if "json" in content_type:
                data = resp.json()
                jobs = data.get("jobs") or data.get("results") or data.get("data") or []
                log.info(f"  [Search] Got {len(jobs)} jobs.")
                return jobs if isinstance(jobs, list) else []
            else:
                # HTML response — parse with BeautifulSoup
                log.info("  [Search] Got HTML response — parsing job cards…")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                return _parse_html_cards(soup, query)
        else:
            log.warning(f"  [Search] HTTP {resp.status_code} for '{query}'")
            return []

    except Exception as exc:
        log.error(f"  [Search] Error for '{query}': {exc}")
        return []


def _parse_html_cards(soup, query: str) -> list[dict]:
    """Fallback: parse job cards from Upwork search HTML response."""
    jobs = []
    cards = (
        soup.find_all("article", class_="job-tile")
        or soup.select("[data-test='job-tile']")
        or soup.select("section.up-card-section")
    )
    for card in cards:
        h2 = card.find("h2") or card.find("h3")
        if not h2:
            continue
        link_tag = h2.find("a")
        title = h2.get_text(strip=True)
        raw_link = link_tag["href"] if (link_tag and "href" in link_tag.attrs) else ""
        url = normalize_upwork_url(raw_link)

        desc_elem = (
            card.find("span", {"data-test": "job-description-text"})
            or card.find("div", class_="job-description-text")
            or card.find("p")
        )
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        skill_elems = card.select("[data-test='TokenClamp JobAttrs'] a") or card.select(".air3-token")
        skills = ", ".join(s.get_text(strip=True) for s in skill_elems) or "N/A"

        exp_elem = card.find(attrs={"data-test": "experience-level"})
        experience = exp_elem.get_text(strip=True) if exp_elem else "N/A"

        time_elem = card.find("span", {"data-test": "posted-on"}) or card.find("small", {"data-test": "job-pubilshed-date"})
        posted = time_elem.get_text(strip=True) if time_elem else "N/A"

        loc_elem = card.find(attrs={"data-test": "client-country"})
        location = loc_elem.get_text(strip=True) if loc_elem else "N/A"

        pay_elem = card.find(attrs={"data-test": "is-payment-verified"}) or card.find(attrs={"data-test": "payment-verification-status"})
        payment_verified = "Yes" if pay_elem else "N/A"

        budget_elem = card.find(attrs={"data-test": "job-type-label"}) or card.find(attrs={"data-test": "budget"})
        budget = budget_elem.get_text(strip=True) if budget_elem else "N/A"

        if url and url != "No link":
            jobs.append({
                "title": title, "url": url, "description": description,
                "skills": skills, "experience": experience, "posted_date": posted,
                "client_location": location, "payment_verified": payment_verified,
                "budget_display": budget, "job_type": "N/A",
                "client_rating": "N/A", "client_spent": "N/A",
                "proposals": "N/A", "category": "N/A", "source_query": query,
            })
    log.info(f"  [Search] Parsed {len(jobs)} cards from HTML.")
    return jobs


def _normalize_api_job(raw: dict, query: str) -> dict | None:
    """Normalise a JSON job result from Upwork's search API."""
    raw_url = raw.get("jobUrl") or raw.get("url") or raw.get("link") or ""
    ciphertext = raw.get("ciphertext") or raw.get("id") or ""
    if not raw_url and ciphertext:
        raw_url = f"https://www.upwork.com/jobs/{ciphertext}/"
    url = normalize_upwork_url(str(raw_url))
    if url == "No link":
        return None

    title = str(raw.get("title") or "Untitled").strip()
    if not title or title == "Untitled":
        return None

    desc = str(raw.get("description") or raw.get("snippet") or "").strip()
    skills_raw = raw.get("skills") or raw.get("attrs") or []
    if isinstance(skills_raw, list):
        skills = ", ".join(s.get("prettyName") or s.get("name") or str(s) for s in skills_raw if s)
    else:
        skills = str(skills_raw)

    job_type = str(raw.get("jobType") or raw.get("type") or "N/A").upper()
    budget = raw.get("budget") or raw.get("rate") or {}
    if isinstance(budget, dict):
        lo = budget.get("min") or budget.get("minimum")
        hi = budget.get("max") or budget.get("maximum")
        currency = budget.get("currencyCode", "$")
        if lo or hi:
            budget_display = f"{currency}{lo or '?'}–{currency}{hi or '?'}"
        else:
            budget_display = "N/A"
    else:
        budget_display = str(budget) if budget else "N/A"

    client = raw.get("client") or raw.get("buyer") or {}
    payment_verified = "Yes" if client.get("paymentVerificationStatus", "").lower() == "verified" or client.get("paymentVerified") else "No"

    return {
        "title":            title,
        "url":              url,
        "description":      desc,
        "job_type":         job_type,
        "budget_display":   budget_display,
        "experience":       str(raw.get("contractorTier") or raw.get("experienceLevel") or "N/A"),
        "posted_date":      str(raw.get("postedOn") or raw.get("publishedOn") or "N/A")[:19].replace("T", " "),
        "client_location":  str(client.get("location", {}).get("country") if isinstance(client.get("location"), dict) else client.get("country") or "N/A"),
        "client_rating":    str(client.get("score") or client.get("rating") or "N/A"),
        "client_spent":     str(client.get("totalCharges") or client.get("totalSpent") or "N/A"),
        "proposals":        str(raw.get("proposalsTier") or raw.get("proposals") or "N/A"),
        "payment_verified": payment_verified,
        "skills":           skills or "N/A",
        "category":         str(raw.get("category2") or raw.get("category") or "N/A"),
        "source_query":     query,
    }


def run_apify_query(search_url: str) -> list[dict]:
    """Runs the flash_mage/upwork actor on Apify and returns the dataset items."""
    if not apify_client:
        log.error("Apify API token missing. Cannot run actor.")
        return []
    
    log.info(f"  [Apify] Calling actor for: {search_url[:60]}...")
    run_input = {
        "startUrls": [{"url": search_url}],
        "maxItems": MAX_PER_QUERY
    }
    try:
        run = apify_client.actor("flash_mage/upwork").call(run_input=run_input)
        if not run:
            return []
        items = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
        log.info(f"  [Apify] Got {len(items)} items.")
        return items
    except Exception as e:
        log.error(f"  [Apify] Error running actor: {e}")
        return []





def _extract_job_from_apify_item(item: dict) -> dict | None:
    """
    Parse a raw flash_mage/upwork actor output item.

    Actual structure (confirmed from live API):
      item["link"]  = job URL
      item["title"] = job title
      item["data"]["opening"] = all job details
      item["data"]["buyer"]   = client info
    """
    # ── URL ───────────────────────────────────────────────────────────────
    raw_url = item.get("link") or item.get("url") or item.get("jobUrl") or ""
    url = normalize_upwork_url(str(raw_url))
    if url == "No link":
        return None

    # ── Title ─────────────────────────────────────────────────────────────
    title = str(item.get("title") or item.get("jobTitle") or "Untitled").strip()
    if not title or title == "Untitled":
        return None

    # ── Nested data ────────────────────────────────────────────────────────
    data    = item.get("data", {}) or {}
    opening = data.get("opening", {}) or {}
    buyer   = data.get("buyer", {}) or {}
    client  = buyer.get("info", {}) or {}
    stats   = buyer.get("stats", {}) or {}
    company = buyer.get("jobs", {}) or {}

    # ── Description ───────────────────────────────────────────────────────
    description = str(opening.get("description") or data.get("description") or "").strip()

    # ── Job type & budget ─────────────────────────────────────────────────
    engagement = opening.get("engagement") or opening.get("engagementType") or ""
    job_type   = "HOURLY" if "hourly" in str(engagement).lower() else "FIXED"

    amount = opening.get("amount") or opening.get("budget") or {}
    if isinstance(amount, dict):
        budget_min = amount.get("min") or amount.get("minimum")
        budget_max = amount.get("max") or amount.get("maximum")
    else:
        budget_min = budget_max = amount if amount else None

    rate = opening.get("hourlyBudgetMin") or opening.get("hourlyRateMin")
    rate_max = opening.get("hourlyBudgetMax") or opening.get("hourlyRateMax")

    if job_type == "FIXED" and (budget_min or budget_max):
        lo = f"${budget_min:,.0f}" if isinstance(budget_min, (int, float)) else str(budget_min or "?")
        hi = f"${budget_max:,.0f}" if isinstance(budget_max, (int, float)) else str(budget_max or "")
        budget_display = f"{lo}–{hi} (Fixed)" if budget_max and budget_min != budget_max else f"{lo} (Fixed)"
    elif rate or rate_max:
        budget_display = f"${rate or '?'}–${rate_max or '?'}/hr"
    else:
        budget_display = "N/A"

    # ── Experience level ──────────────────────────────────────────────────
    tier_map = {"BASIC": "Entry Level", "INTERMEDIATE": "Intermediate", "EXPERT": "Expert"}
    tier_raw = opening.get("contractorTier") or opening.get("experienceLevel") or ""
    experience = tier_map.get(str(tier_raw).upper(), str(tier_raw) or "N/A")

    # ── Posted date ───────────────────────────────────────────────────────
    posted_raw = opening.get("postedOn") or opening.get("publishTime") or opening.get("createdAt") or ""
    posted_date = str(posted_raw)[:19].replace("T", " ") if posted_raw else "N/A"

    # ── Client / buyer info ───────────────────────────────────────────────
    client_location = (
        client.get("location", {}) or {}
    ).get("country") or stats.get("location") or "N/A"

    client_rating = stats.get("score") or stats.get("rating")
    client_spent_raw = stats.get("totalCharges") or stats.get("totalSpent") or company.get("totalCharges")
    client_spent = f"${client_spent_raw:,.0f}" if isinstance(client_spent_raw, (int, float)) else str(client_spent_raw or "N/A")

    proposals = opening.get("proposalsTier") or opening.get("proposals") or data.get("proposals")
    payment_ver = (client.get("paymentVerificationStatus") or "").lower() == "verified" \
               or stats.get("paymentVerified") is True \
               or buyer.get("isPaymentMethodVerified") is True

    # ── Skills ────────────────────────────────────────────────────────────
    skills_raw = opening.get("skills") or data.get("skills") or []
    if isinstance(skills_raw, list):
        skills = ", ".join(
            s.get("name") or s.get("prettyName") or str(s)
            for s in skills_raw if s
        )
    else:
        skills = str(skills_raw)

    # ── Category ──────────────────────────────────────────────────────────
    cat_raw = opening.get("occupation") or opening.get("category2") or data.get("category") or {}
    if isinstance(cat_raw, dict):
        category = cat_raw.get("prefLabel") or cat_raw.get("name") or "N/A"
    else:
        category = str(cat_raw) or "N/A"

    return {
        "title":            title,
        "url":              url,
        "description":      description,
        "job_type":         job_type,
        "budget_display":   budget_display,
        "experience":       experience,
        "posted_date":      posted_date,
        "client_location":  client_location,
        "client_rating":    str(client_rating) if client_rating else "N/A",
        "client_spent":     client_spent,
        "proposals":        str(proposals) if proposals else "N/A",
        "payment_verified": "Yes" if payment_ver else "No",
        "skills":           skills or "N/A",
        "category":         category,
        "source_query":     "",
    }


def collect_all_jobs(seen_manager: SeenJobsManager) -> list[dict]:
    """
    Run all SEARCH_URLS through the Apify actor and collect raw jobs.
    Deduplicates across queries and skips already-seen jobs.
    """
    all_jobs:   list[dict] = []
    seen_urls:  set        = set()
    skipped_seen           = 0

    for search_url in SEARCH_URLS:
        raw_items = run_apify_query(search_url)

        for item in raw_items:
            job = _extract_job_from_apify_item(item)
            if not job:
                continue

            url    = job["url"]
            job_id = SeenJobsManager.make_id(url)

            if url in seen_urls:
                continue
            seen_urls.add(url)

            if seen_manager.is_seen(job_id):
                skipped_seen += 1
                continue

            # Label the source query (readable keyword)
            q_label = _up.parse_qs(_up.urlparse(search_url).query).get("q", [search_url])[0]
            job["source_query"] = q_label
            all_jobs.append(job)

        log.info(f"  Running total: {len(all_jobs)} unique new jobs collected.")
        time.sleep(3)

    log.info(f"\nTotal raw jobs collected: {len(all_jobs)}  |  Skipped (seen): {skipped_seen}")
    return all_jobs


# ─────────────────────────────────────────────────────────────────────────────
# GROQ AI EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────
def _parse_retry_after(error_str: str) -> float | None:
    m = re.search(r"try again in\s+(?:(\d+)m)?(?:([\d.]+)s)?", str(error_str))
    if m:
        return int(m.group(1) or 0) * 60 + float(m.group(2) or 0)
    return None


def _call_groq(prompt: str, model: str) -> dict:
    completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a JSON-only API. Output strictly valid JSON."},
            {"role": "user",   "content": prompt},
        ],
        model=model,
        response_format={"type": "json_object"},
    )
    return json.loads(completion.choices[0].message.content)


def evaluate_job_with_groq(job: dict) -> dict:
    """
    Evaluate a job with Groq AI.
    Returns enriched dict: is_engineering, score (0-100), and Arabic text fields.
    """
    description = job.get("description", "")[:700]

    client_ctx = (
        f"Payment: {job.get('payment_verified', 'N/A')}, "
        f"Rating: {job.get('client_rating', 'N/A')}/5, "
        f"Total spent: {job.get('client_spent', 'N/A')}"
    )
    extra_ctx = ""
    if job.get("budget_display") and job["budget_display"] != "N/A":
        extra_ctx += f"\nBudget: {job['budget_display']}"
    if job.get("skills") and job["skills"] != "N/A":
        extra_ctx += f"\nSkills: {job['skills'][:200]}"

    prompt = f"""Evaluate this Upwork job for an architecture/engineering freelancer.
Score 0-100. Higher = better opportunity.

SCORING (priority order):
1. Relevance: Architecture, Interior Design, BIM, AutoCAD, Revit, 3D Rendering, Visualization.
2. Budget size relative to scope.
3. Client quality: payment verified + high rating + spend history = higher score.

RULES:
- is_engineering=true for ANY: Civil/Building Architecture, Interior Design, MEP, BIM,
  Structural, AutoCAD, 3D Architectural Rendering, Exterior/Interior Visualization,
  Space Planning, Landscape Architecture, Construction Drawings, Floor Plans,
  SketchUp/Revit/Lumion/Rhino/3ds Max work, Renovation Design.
- is_engineering=false ONLY for: Pure Software/IT, Web/App dev, Data Science, ML,
  E-commerce, Jewelry design, Game development (unless architectural visualization).
- When in doubt about a design job, set is_engineering=true.
- Never return null. Estimate if info is missing.
- All text fields in Arabic EXCEPT budget field (use $ amount).

{client_ctx}{extra_ctx}

Return ONLY valid JSON, no markdown:
{{"is_engineering":bool,"score":int,"score_reason":"arabic text","budget":"$amount or غير محدد","duration":"arabic","client_status":"arabic","software_needed":"arabic"}}

Job title: {job.get('title', '')}
Job description: {description}"""

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
                        log.warning(f"  {model_label} daily limit hit. Switching model…")
                        break
                    if retry_after and waits_done < max_waits:
                        wait = int(retry_after) + 5
                        log.info(f"  Rate limit on {model_label}. Waiting {wait}s…")
                        for remaining in range(wait, 0, -10):
                            print(f"     …{remaining}s remaining", end="\r")
                            time.sleep(min(10, remaining))
                        print("  Wait complete. Retrying…               ")
                        waits_done += 1
                        continue
                    else:
                        log.warning(f"  {model_label} rate limited. Switching model…")
                        break
                else:
                    log.error(f"  Groq error ({model_label}): {exc}")
                    return error_default

    log.error("  All Groq models exhausted. Skipping job.")
    return error_default


# ─────────────────────────────────────────────────────────────────────────────
# EXCEL EXPORT
# ─────────────────────────────────────────────────────────────────────────────
def safe_str(val) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "غير محدد"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def prepare_row(job: dict) -> dict:
    return {
        "المنصة":              "Upwork",
        "الرابط":              job["url"],
        "التاريخ":             safe_str(job.get("posted_date", "N/A")),
        "التصنيف":             safe_str(job.get("category", "N/A")),
        "العنوان":             job["title"],
        "المهارات":            safe_str(job.get("skills", "N/A")),
        "الخبرة المطلوبة":     safe_str(job.get("experience", "N/A")),
        "الموقع":              safe_str(job.get("client_location", "N/A")),
        "العروض":              safe_str(job.get("proposals", "N/A")),
        "الدفع موثق":          safe_str(job.get("payment_verified", "N/A")),
        "الميزانية":           safe_str(job.get("budget", "غير محدد")),
        "العميل":              safe_str(job.get("client_status", "غير محدد")),
        "المدة":               safe_str(job.get("duration", "غير محدد")),
        "البرامج":             safe_str(job.get("software", "غير محدد")),
        "البحث المستخدم":      safe_str(job.get("source_query", "")),
        "التقييم":             f"Score: {job.get('score', 0)}/100 — {safe_str(job.get('score_reason', ''))}",
    }


def format_worksheet(worksheet, df, workbook, is_top: bool = False):
    worksheet.right_to_left()

    header_color = "#0D5E3F" if is_top else "#1F4E78"
    header_fmt = workbook.add_format({
        "bold": True, "text_wrap": True, "valign": "vcenter",
        "align": "center", "fg_color": header_color,
        "font_color": "white", "border": 1, "font_size": 11,
    })
    cell_fmt = workbook.add_format({
        "align": "center", "valign": "vcenter",
        "text_wrap": True, "border": 1, "font_size": 10,
    })
    link_fmt = workbook.add_format({
        "align": "center", "valign": "vcenter",
        "font_color": "#0563C1", "underline": 1,
        "border": 1, "font_size": 10,
    })
    score_hi_fmt = workbook.add_format({
        "align": "center", "valign": "vcenter", "text_wrap": True,
        "border": 1, "font_size": 10, "fg_color": "#1A7A42", "font_color": "white", "bold": True,
    })
    score_mid_fmt = workbook.add_format({
        "align": "center", "valign": "vcenter", "text_wrap": True,
        "border": 1, "font_size": 10, "fg_color": "#E07B00", "font_color": "white",
    })

    col_widths = [10, 42, 20, 25, 45, 35, 20, 18, 12, 12, 22, 28, 18, 28, 30, 70]
    for col_num, (header, width) in enumerate(zip(df.columns.values, col_widths)):
        worksheet.write(0, col_num, header, header_fmt)
        worksheet.set_column(col_num, col_num, width)

    for row_idx in range(1, len(df) + 1):
        worksheet.set_row(row_idx, 50)
        for col_idx, col_name in enumerate(df.columns):
            val = df.iloc[row_idx - 1, col_idx]
            val_str = safe_str(val)

            if col_name == "الرابط" and val_str.startswith("http"):
                worksheet.write_url(row_idx, col_idx, val_str, link_fmt, "رابط الوظيفة")
            elif col_name == "التقييم":
                # Colour-code score column
                score_match = re.search(r"Score:\s*(\d+)", val_str)
                score_val   = int(score_match.group(1)) if score_match else 0
                fmt = score_hi_fmt if score_val >= 70 else (score_mid_fmt if score_val >= 45 else cell_fmt)
                worksheet.write(row_idx, col_idx, val_str, fmt)
            else:
                worksheet.write(row_idx, col_idx, val_str, cell_fmt)


def export_to_excel(all_jobs: list[dict], top_jobs: list[dict]):
    df_all = pd.DataFrame([prepare_row(j) for j in all_jobs])
    df_top = pd.DataFrame([prepare_row(j) for j in top_jobs])

    all_sheet = f"All Jobs ({len(all_jobs)})"
    top_sheet = f"Top {len(top_jobs)} Jobs"

    writer = None
    try:
        writer = pd.ExcelWriter(EXCEL_FILE_NAME, engine="xlsxwriter")
        df_all.to_excel(writer, index=False, sheet_name=all_sheet)
        df_top.to_excel(writer, index=False, sheet_name=top_sheet)

        wb = writer.book
        format_worksheet(writer.sheets[all_sheet], df_all, wb, is_top=False)
        format_worksheet(writer.sheets[top_sheet], df_top, wb, is_top=True)
    except Exception as exc:
        log.error(f"Excel write error: {exc}")
        raise
    finally:
        if writer:
            writer.close()

    log.info(f"Excel saved: {EXCEL_FILE_NAME}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 70)
    log.info("   UPWORK ARCHITECTURAL DESIGN JOB SCRAPER v3 — STARTING")
    log.info("   Method: Apify flash_mage/upwork (residential proxies)")
    log.info(f"  Target: {TARGET_JOBS} engineering jobs  |  Top: {TOP_N}")
    log.info("=" * 70)

    seen_manager = SeenJobsManager(SEEN_JOBS_FILE)

    # ── Step 1: Collect raw jobs via Apify ────────────────────────────────
    log.info(f"\n[Step 1] Running {len(SEARCH_URLS)} Apify queries with targeted Upwork URLs…")
    raw_jobs = collect_all_jobs(seen_manager)

    log.info(f"\nRaw jobs collected: {len(raw_jobs)}")

    if not raw_jobs:
        log.error(
            "\nNo jobs returned from Apify.\n"
            "Troubleshooting:\n"
            "  1. Check APIFY_API_TOKEN in .env is valid.\n"
            "  2. Check your Apify account has credit (free = $5/month).\n"
            "  3. The flash_mage/upwork actor may be temporarily down.\n"
            "     Try: https://console.apify.com/actors/flash_mage~upwork\n"
        )
        return

    # ── Step 2: AI evaluation ─────────────────────────────────────────────
    log.info(f"\n[Step 2] AI-evaluating {len(raw_jobs)} jobs (target: {TARGET_JOBS} engineering)…")
    analyzed_jobs: list[dict] = []

    for i, job in enumerate(raw_jobs):
        if len(analyzed_jobs) >= TARGET_JOBS:
            log.info(f"Target of {TARGET_JOBS} engineering jobs reached.")
            break

        log.info(f"  [{i+1}/{len(raw_jobs)}] {job['title'][:65]}")
        ai = evaluate_job_with_groq(job)

        if ai.get("is_engineering"):
            analyzed_jobs.append({
                **job,
                "score":         ai.get("score", 0),
                "score_reason":  ai.get("score_reason", "مواصفات مناسبة"),
                "budget":        ai.get("budget", job.get("budget_display", "غير محدد")),
                "duration":      ai.get("duration", "غير محدد"),
                "client_status": ai.get("client_status", "غير محدد"),
                "software":      ai.get("software_needed", "غير محدد"),
            })
            log.info(
                f"  --> Engineering job! Score={ai.get('score', 0)}  "
                f"Total: {len(analyzed_jobs)}/{TARGET_JOBS}"
            )
        else:
            log.info("  --> Not engineering, skipped.")

        time.sleep(GROQ_RATE_LIMIT_DELAY)

    if not analyzed_jobs:
        log.error("\nNo engineering jobs found after AI evaluation.")
        return

    if len(analyzed_jobs) < TARGET_JOBS:
        log.warning(
            f"Only {len(analyzed_jobs)} engineering jobs found "
            f"(target: {TARGET_JOBS}). Continuing with available data."
        )

    # ── Step 3: Mark as seen ──────────────────────────────────────────────
    for job in analyzed_jobs:
        seen_manager.mark_seen(SeenJobsManager.make_id(job["url"]))

    # ── Step 4: Sort & select Top N ───────────────────────────────────────
    log.info("\n[Step 3] Sorting by AI score…")
    all_sorted = sorted(analyzed_jobs, key=lambda j: j.get("score", 0), reverse=True)
    top_n      = all_sorted[:TOP_N]

    log.info(f"\nTop {len(top_n)} jobs by score:")
    for rank, j in enumerate(top_n, 1):
        log.info(f"  {rank:>2}. [{j.get('score', 0):>3}/100]  {j['title'][:65]}")

    # ── Step 5: Export to Excel ───────────────────────────────────────────
    log.info(f"\n[Step 4] Exporting to {EXCEL_FILE_NAME}…")
    export_to_excel(all_sorted, top_n)

    log.info("\n" + "=" * 70)
    log.info(f"  DONE!  {len(all_sorted)} jobs exported to {EXCEL_FILE_NAME}")
    log.info("=" * 70)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
