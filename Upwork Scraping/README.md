# Upwork Architectural Design Jobs Scraper

A **production-ready** Python web scraper that collects architectural design job listings from Upwork and exports them to a professionally formatted Excel workbook.

---

## Features

| Feature | Details |
|---|---|
| 🎯 Smart Search | 10 targeted queries covering all required skill combinations |
| 🤖 Bot Avoidance | Randomized delays, User-Agent rotation, browser-like headers |
| 🔁 Dual Engine | Requests-based scraper with automatic Selenium fallback |
| 🧠 Relevance Scoring | Keyword + budget + client history + proposal count scoring |
| 📋 Deduplication | `seen_jobs.json` tracks all scraped URLs across runs |
| 📊 Excel Export | Two formatted tabs, clickable hyperlinks, frozen headers, auto-filter |

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install requests beautifulsoup4 lxml selenium webdriver-manager openpyxl fake-useragent
```

### 2. Google Chrome
The Selenium fallback requires **Google Chrome** to be installed.  
ChromeDriver is installed **automatically** via `webdriver-manager`.

---

## Usage

```bash
cd "E:\MY PROJECT\Machine Learning\Upwork Scraping"
python upwork_scraper.py
```

The script will:
1. Try requests-based scraping first (fast, no browser needed)
2. Auto-switch to Selenium if Upwork blocks requests
3. Search across 10 query terms to collect 35+ unique jobs
4. Score and rank all jobs by relevance
5. Export results to `Upwork_Architectural_Jobs.xlsx`

---

## Output Files

| File | Description |
|---|---|
| `Upwork_Architectural_Jobs.xlsx` | Main output — two tabs |
| `seen_jobs.json` | Deduplication database (do not delete between runs) |
| `upwork_scraper.log` | Full execution log |

### Excel Tab Structure

**Tab 1 — `All_35_Jobs`**
- All collected jobs sorted by relevance score (highest first)
- Blue header theme

**Tab 2 — `Top_15_Selected`**
- The 15 highest-scoring jobs
- Green header theme, rank numbers in job titles

**Columns in both tabs:**

| Column | Description |
|---|---|
| Job Title | Full title (hyperlinked to Upwork listing in URL column) |
| Job URL | **Clickable hyperlink** directly to the job posting |
| Job Type | Fixed-price or Hourly |
| Budget / Rate | Posted budget or hourly rate range |
| Experience Level | Entry / Intermediate / Expert |
| Skills / Tags | All skill tags on the listing |
| Category | Upwork job category |
| Description | Full job description (up to 800 chars) |
| Posted Date | Relative posting date |
| Client Location | Country of the client |
| Client Rating | Average rating of the client |
| Client Total Spent | Total amount spent by client on Upwork |
| Proposals Count | Number of bids received |
| Search Query Used | Which search query found this job |
| Scraped At | Timestamp of scraping |
| Relevance Score | 0–100 score based on keyword/budget/client signals |

---

## Configuration

All settings are in the `CONFIG` dict at the top of `upwork_scraper.py`:

```python
CONFIG = {
    "target_job_count":    35,      # Minimum jobs to collect
    "delay_min":           3.5,     # Min seconds between requests
    "delay_max":           8.0,     # Max seconds between requests
    "selenium_headless":   True,    # Set False to watch the browser
    "use_selenium_fallback": True,  # Auto-switch to Selenium if needed
    ...
}
```

### Tips for getting more results

- Set `"selenium_headless": False` to watch what's happening in the browser
- Run the script at different times of day if blocked
- Increase `"delay_min"` and `"delay_max"` if getting rate-limited
- If completely blocked: log in to Upwork in Chrome manually first,  
  then run the script — the cookies persist and reduce bot signals

---

## Deduplication

A `seen_jobs.json` file tracks all scraped job URLs (as MD5 hashes).

- **First run:** collects all 35+ jobs
- **Subsequent runs:** skips any jobs already in `seen_jobs.json` and collects only new listings
- To reset (start fresh): delete `seen_jobs.json`

---

## Relevance Scoring System

Scores range from **0 to 100**:

| Range | Interpretation |
|---|---|
| 70–100 | 🟢 Highly relevant — strong match |
| 45–69 | 🟡 Moderately relevant |
| 0–44 | ⚪ Lower relevance |

**Score components:**
- Keyword density: up to 50 pts (title + description + skills)
- Budget clarity: up to 20 pts
- Client history signals: up to 15 pts
- Proposal count (fewer = better): up to 15 pts

---

## Troubleshooting

**Problem:** Script collects 0 jobs  
**Solution:** Upwork is actively blocking. Try:
- Setting `"selenium_headless": False` to see the browser
- Running at off-peak hours
- Logging into Upwork in Chrome before running

**Problem:** ChromeDriver error  
**Solution:** Make sure Google Chrome is installed and up to date. `webdriver-manager` will handle the driver automatically.

**Problem:** Very slow execution  
**Reason:** Intentional — delays are required to avoid bans. Do not reduce them below 2 seconds.

---

## Legal & Ethical Notice

This script is intended for personal use and research.  
Always check [Upwork's Terms of Service](https://www.upwork.com/legal) before scraping.  
Use responsibly: do not run this at high frequency or in bulk commercial contexts.
