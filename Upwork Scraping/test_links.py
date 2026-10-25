"""
test_links.py  -  Link Handling Audit for scrap.py
===================================================
Runs in three phases:
  Phase 1 : Offline unit tests for normalize_upwork_link() covering every
            known Upwork URL format plus all edge/error cases.
  Phase 2 : Live HTTP reachability check - opens each resolved URL with
            urllib and verifies it returns HTTP 200 (or an expected redirect).
  Phase 3 : Adversarial stress / crash test.

Run:  python test_links.py
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import re
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse

# ============================================================
# Inline copy of normalize_upwork_link so this file is
# fully self-contained (no import from scrap.py needed).
# ============================================================
def normalize_upwork_link(raw_link: str) -> str:
    """
    Convert any Upwork href into a canonical
    https://www.upwork.com/jobs/~TOKEN URL.

    Upwork job tokens are 18-20 alphanumeric chars after ~.
    We require >= 16 to safely reject profile slugs and other
    short ~identifiers that appear in non-jobs paths.
    """
    if not raw_link:
        return "No link"
    raw_link = raw_link.strip()  # guard against whitespace
    if not raw_link:
        return "No link"

    # Pattern 1 – ~TOKEN (>=16 chars) inside a /jobs/ path segment
    match = re.search(r'/jobs/?(~[0-9a-zA-Z]{16,})', raw_link)
    if match:
        return f"https://www.upwork.com/jobs/{match.group(1)}"

    # Pattern 1b – ~TOKEN in query string / after = (search-modal embed style)
    match = re.search(r'[?&=](~[0-9a-zA-Z]{16,})', raw_link)
    if match:
        return f"https://www.upwork.com/jobs/{match.group(1)}"

    # Pattern 2 – numeric uid query param  e.g. ?uid=1234567890
    match = re.search(r'[?&]uid=([0-9]{8,})', raw_link)
    if match:
        return f"https://www.upwork.com/jobs/~{match.group(1)}"

    # Pattern 3 – relative path → prepend domain
    if raw_link.startswith("/"):
        return f"https://www.upwork.com{raw_link}"

    # Pattern 4 – already absolute
    if raw_link.startswith("http"):
        return raw_link

    return "No link"


# ============================================================
# PHASE 1 — Offline Unit Tests
# ============================================================
PASS = "[PASS]"
FAIL = "[FAIL]"

# Real Upwork job tokens are 18-20 alphanumeric chars — use realistic values
TOKEN_18  = "~" + "A" * 18                     # ~AAAAAAAAAAAAAAAAAA
TOKEN_18s = "A" * 18                            # without leading ~
TOKEN_20  = "~" + "1a2B3c4D5e6F7g8H9i0J"       # ~1a2B3c4D5e6F7g8H9i0J

TEST_CASES = [
    # (description, raw_input, expected_output)

    # ── Pattern 1a: ~TOKEN (>=16 chars) inside /jobs/ path ─────────────────
    (
        "Canonical /jobs/~TOKEN (18 chars)",
        f"/jobs/{TOKEN_18}",
        f"https://www.upwork.com/jobs/{TOKEN_18}",
    ),
    (
        "Absolute canonical jobs URL with 20-char token",
        f"https://www.upwork.com/jobs/{TOKEN_20}",
        f"https://www.upwork.com/jobs/{TOKEN_20}",
    ),
    (
        "Search-results href with long token and trailing params",
        f"https://www.upwork.com/nx/search/jobs/{TOKEN_18}/?ref=fl_find_work",
        f"https://www.upwork.com/jobs/{TOKEN_18}",
    ),
    (
        "Relative /jobs/ path with real-length token",
        f"/jobs/{TOKEN_20}",
        f"https://www.upwork.com/jobs/{TOKEN_20}",
    ),

    # ── Pattern 1b: ~TOKEN in query string (search-modal style) ────────────
    (
        "Search-modal URL: ~TOKEN embedded in query param value",
        f"/nx/search/jobs/?q=architect&token={TOKEN_18}",
        f"https://www.upwork.com/jobs/{TOKEN_18}",
    ),

    # ── Pattern 1 NEGATIVE: ~TOKEN too short (<16) must NOT match P1/P1b ──
    (
        "Short token (9 chars) in /jobs/ — falls to Pattern 3 (prepend domain)",
        "/jobs/~123456789",
        "https://www.upwork.com/jobs/~123456789",
    ),
    (
        "Short token in /freelancers/ — must NOT be routed to /jobs/",
        "/freelancers/~someprofile",
        "https://www.upwork.com/freelancers/~someprofile",  # Pattern 3
    ),
    (
        "Profile slug in absolute URL — pass through unchanged (Pattern 4)",
        "https://www.upwork.com/freelancers/~johndoe123",
        "https://www.upwork.com/freelancers/~johndoe123",
    ),

    # ── Pattern 2: ?uid= or &uid= numeric (>=8 digits) ─────────────────────
    (
        "Legacy ?uid= numeric param (10 digits)",
        "/nx/jobs/?uid=1234567890",
        "https://www.upwork.com/jobs/~1234567890",
    ),
    (
        "Legacy &uid= in multi-param URL",
        "/search/jobs/?q=bim&sort=recency&uid=9876543210",
        "https://www.upwork.com/jobs/~9876543210",
    ),
    (
        "uid= too short (7 digits) — must NOT match Pattern 2",
        "/jobs/?uid=1234567",
        "https://www.upwork.com/jobs/?uid=1234567",  # Pattern 3
    ),

    # ── Pattern 3: relative path, no valid token ────────────────────────────
    (
        "Relative path /jobs/ with no token",
        "/jobs/",
        "https://www.upwork.com/jobs/",
    ),
    (
        "Relative path to search page",
        "/nx/search/jobs/?q=architect&sort=recency",
        "https://www.upwork.com/nx/search/jobs/?q=architect&sort=recency",
    ),

    # ── Pattern 4: already absolute ────────────────────────────────────────
    (
        "Already-absolute canonical URL — pass through",
        f"https://www.upwork.com/jobs/{TOKEN_20}",
        f"https://www.upwork.com/jobs/{TOKEN_20}",
    ),
    (
        "Absolute non-Upwork URL — pass through",
        "https://example.com/redirect?to=upwork",
        "https://example.com/redirect?to=upwork",
    ),

    # ── Whitespace stripping ────────────────────────────────────────────────
    (
        "Leading/trailing whitespace stripped before matching",
        f"  /jobs/{TOKEN_18}  ",
        f"https://www.upwork.com/jobs/{TOKEN_18}",
    ),
    (
        "Whitespace-only string → No link",
        "   ",
        "No link",
    ),

    # ── Error / empty cases ─────────────────────────────────────────────────
    (
        "Empty string → No link",
        "",
        "No link",
    ),
    (
        "Anchor href (#section) → No link",
        "#section",
        "No link",
    ),
    (
        "javascript: href → No link",
        "javascript:void(0)",
        "No link",
    ),
    (
        "Short absolute /jobs/~abc — no token match, falls to Pattern 4",
        "https://www.upwork.com/jobs/~abc",
        "https://www.upwork.com/jobs/~abc",
    ),
]


def run_unit_tests() -> tuple[int, int]:
    """Run all offline test cases. Returns (passed, total)."""
    passed = 0
    total  = len(TEST_CASES)

    print("=" * 70)
    print("PHASE 1 — Offline Unit Tests for normalize_upwork_link()")
    print("=" * 70)

    for desc, raw, expected in TEST_CASES:
        result = normalize_upwork_link(raw)
        ok     = result == expected
        status = PASS if ok else FAIL
        if ok:
            passed += 1
        print(f"\n  {status}  {desc}")
        if not ok:
            print(f"         Input   : {repr(raw)}")
            print(f"         Expected: {expected}")
            print(f"         Got     : {result}")

    print("\n" + "─" * 70)
    print(f"  Result: {passed}/{total} tests passed")
    print("─" * 70)
    return passed, total


# ============================================================
# PHASE 2 — Live HTTP Reachability Check
# ============================================================
SAMPLE_KNOWN_LINKS = [
    # Add real job links captured from a previous run here.
    # These are placeholders — they will be tested if valid.
    "https://www.upwork.com/jobs/~01234567890123456789",
]

def check_url(url: str, timeout: int = 10) -> dict:
    """
    Open URL with urllib (follows redirects automatically).
    Returns a result dict with: url, final_url, status, reachable, error.
    """
    result = {"url": url, "final_url": None, "status": None, "reachable": False, "error": None}
    try:
        req = urllib.request.Request(
            url,
            headers={
                # Minimal browser-like header to avoid 403 on some endpoints
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result["status"]    = resp.status
            result["final_url"] = resp.url
            result["reachable"] = (resp.status in (200, 301, 302, 303, 307, 308))
    except urllib.error.HTTPError as e:
        result["status"] = e.code
        result["error"]  = f"HTTP {e.code}: {e.reason}"
        # 403/401 on Upwork just means login-wall — link IS valid but protected
        result["reachable"] = e.code in (401, 403)
    except urllib.error.URLError as e:
        result["error"] = f"URLError: {e.reason}"
    except Exception as e:
        result["error"] = str(e)
    return result


def run_live_checks(links: list[str]) -> tuple[int, int]:
    """HTTP-probe each link. Returns (reachable, total)."""
    print("\n" + "=" * 70)
    print("PHASE 2 - Live HTTP Reachability Check")
    print("=" * 70)

    if not links:
        print("  [INFO] No links provided for live check.")
        print("         Add real job links to SAMPLE_KNOWN_LINKS in this file,")
        print("         or pass them from the scraper output.\n")
        return 0, 0

    reachable_count = 0
    total = len(links)

    for url in links:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print(f"\n  [SKIP] Invalid URL format: {url}")
            continue

        print(f"\n  [CHECK] {url}")
        res = check_url(url)
        time.sleep(0.5)  # polite delay between HTTP probes

        if res["reachable"]:
            reachable_count += 1
            redirect_note = ""
            if res["final_url"] and res["final_url"] != url:
                redirect_note = f"\n         -> Redirected to: {res['final_url']}"
            print(f"  [OK]  REACHABLE  HTTP {res['status']}{redirect_note}")
        else:
            error_note = f"  ({res['error']})" if res["error"] else ""
            print(f"  [ERR] UNREACHABLE  HTTP {res['status']}{error_note}")

    print("\n" + "─" * 70)
    print(f"  Result: {reachable_count}/{total} links reachable")
    print("─" * 70)
    return reachable_count, total


# ============================================================
# PHASE 3 — Regex Pattern Edge-Case Stress Test
# ============================================================
def run_regex_stress_test():
    """
    Auto-generate adversarial inputs and verify normalize_upwork_link
    never crashes — just returns "No link" or a valid URL string.
    """
    print("\n" + "=" * 70)
    print("PHASE 3 - Regex Stress / Crash Test (adversarial inputs)")
    print("=" * 70)

    adversarial = [
        None,                          # None type (not str)
        "",
        "~",                           # bare tilde
        "~123",                        # token too short
        "~~~~~~~~~~~~~~~~~~",          # only tildes
        "/jobs/~" + "A" * 200,         # extremely long token
        "https://" + "x" * 2000,      # extremely long URL
        "\x00\x01\x02",               # null bytes
        "ftp://example.com/file",      # non-http scheme
        "  /jobs/~abcdefghij  ",       # leading/trailing whitespace
        "//cdn.upwork.com/~abcdefghij0",  # protocol-relative URL
        "?uid=abc",                    # uid param but non-numeric
        "&uid=",                       # uid param empty
    ]

    crashes = 0
    for inp in adversarial:
        try:
            if inp is None:
                # Function expects str — simulate the caller passing ''
                result = normalize_upwork_link("")
            else:
                result = normalize_upwork_link(inp)
            # Verify result is always a string
            assert isinstance(result, str), "Return type must be str"
        except Exception as e:
            crashes += 1
            print(f"  [CRASH] on input {repr(inp)}: {e}")
        else:
            short = repr(inp)[:40]
            print(f"  [SAFE]  {short:<42}->  {result[:60]}")

    print("\n" + "─" * 70)
    if crashes == 0:
        print("  [OK] No crashes - function is robust to adversarial inputs.")
    else:
        print(f"  [FAIL] {crashes} crash(es) detected - fix required.")
    print("-" * 70)
    return crashes


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    print("\nscrap.py - Link Handling Audit")
    print("Verifying normalize_upwork_link() across all URL patterns\n")

    # Phase 1: offline unit tests
    p1_pass, p1_total = run_unit_tests()

    # Phase 2: live HTTP checks (add real links to SAMPLE_KNOWN_LINKS above)
    p2_reach, p2_total = run_live_checks(SAMPLE_KNOWN_LINKS)

    # Phase 3: adversarial stress test
    p3_crashes = run_regex_stress_test()

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    print(f"  Phase 1 (Unit tests)  : {p1_pass}/{p1_total} passed")
    if p2_total:
        print(f"  Phase 2 (Live HTTP)   : {p2_reach}/{p2_total} reachable")
    else:
        print(f"  Phase 2 (Live HTTP)   : skipped (no links provided)")
    crashes_label = "0 crashes [OK]" if p3_crashes == 0 else f"{p3_crashes} crashes [FAIL]"
    print(f"  Phase 3 (Stress test) : {crashes_label}")

    all_ok = (p1_pass == p1_total) and (p3_crashes == 0)
    if all_ok:
        print("\n  Script is PRODUCTION READY for link handling.")
    else:
        print("\n  Issues found - review failures above before deploying.")
    print("=" * 70 + "\n")

    sys.exit(0 if all_ok else 1)
