"""
============================================================================
Facebook Page Post Scraper — Chinese Embassy in Egypt
============================================================================
Purpose:
    Scrapes posts from a target Facebook Page using the Apify platform,
    strictly filters them to May, June, and July 2026, extracts a defined
    set of fields for academic analysis, and exports the cleaned dataset
    to an Excel file (Chinese_Embassy_FB_Data.xlsx).

Requirements:
    pip install apify-client pandas openpyxl requests

Author note:
    Insert your Apify API token in the APIFY_API_TOKEN variable below
    (or set it as an environment variable APIFY_API_TOKEN — recommended
    so you never hard-code secrets into a script you might share).
============================================================================
"""

import os
import sys
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any

import requests
import pandas as pd
from apify_client import ApifyClient
from apify_client.errors import ApifyApiError

# ----------------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------------

# Replace with your actual token from https://console.apify.com/account/integrations
APIFY_API_TOKEN: str = os.environ.get("APIFY_API_TOKEN", "")

# The canonical page URL
PAGE_URL: str = "https://www.facebook.com/USEmbassyCairo"

# Apify Actor to use. "apify/facebook-posts-scraper" is currently the most
# stable, actively maintained actor for scraping posts (not just page metadata)
# from a public Facebook Page or Profile.
ACTOR_ID: str = "apify/facebook-posts-scraper"

# Strict date window for this research project (inclusive)
DATE_START: date = date(2026, 5, 1)
DATE_END: date = date(2026, 7, 31)

# Safety cap so a misconfigured run doesn't scrape the entire page history.
# The actor will stop once it has gathered posts older than this many days,
# giving the API-level filter a head start before we do the strict pandas
# filter below. Adjust upward if the page posts infrequently.
MAX_POSTS_TO_FETCH: int = 500

OUTPUT_FILENAME: str = "US_Embassy_Cairo_FB_Data.xlsx"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("fb_scraper")


# ----------------------------------------------------------------------------
# 2. RESOLVE THE CANONICAL PAGE URL
# ----------------------------------------------------------------------------
def resolve_canonical_url(share_link: str) -> str:
    """
    Facebook 'share' links (facebook.com/share/...) redirect to the actual
    page/profile URL. Apify's actor generally needs a clean, canonical URL
    (e.g. facebook.com/PageName) to reliably resolve the target, so we
    follow redirects here first rather than passing the share link as-is.
    """
    try:
        logger.info("Resolving canonical URL from share link...")
        response = requests.get(
            share_link,
            allow_redirects=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        final_url = response.url.split("?")[0]  # strip tracking query params
        if "facebook.com" not in final_url:
            logger.warning(
                "Redirect did not land on facebook.com (%s). "
                "Falling back to original link.", final_url
            )
            return share_link
        logger.info("Resolved canonical page URL: %s", final_url)
        return final_url
    except requests.RequestException as e:
        logger.warning(
            "Could not resolve share link (%s). Falling back to raw link. "
            "You may need to manually resolve and hard-code the canonical URL.",
            e,
        )
        return share_link


# ----------------------------------------------------------------------------
# 3. RUN THE APIFY ACTOR
# ----------------------------------------------------------------------------
def run_facebook_scraper(client: ApifyClient, page_url: str) -> List[Dict[str, Any]]:
    """
    Calls the Apify Facebook Posts Scraper actor and returns the raw
    dataset items. Includes an actor-level date hint (onlyPostsNewerThan)
    to reduce scraping cost/time; the authoritative date filter is still
    applied afterwards in pandas (see filter_by_date_range).
    """
    run_input = {
        "startUrls": [{"url": page_url}],
        # Actor-level early-cutoff hint: stop paginating once posts are
        # older than the start of our target window. Format accepted by
        # this actor is YYYY-MM-DD.
        "onlyPostsNewerThan": DATE_START.strftime("%Y-%m-%d"),
        "resultsLimit": MAX_POSTS_TO_FETCH,
    }

    try:
        logger.info("Starting Apify actor run: %s", ACTOR_ID)
        run = client.actor(ACTOR_ID).call(run_input=run_input)
    except ApifyApiError as e:
        logger.error("Apify API error while running actor: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error while running actor: %s", e)
        sys.exit(1)

    if isinstance(run, dict):
        dataset_id = run.get("defaultDatasetId")
    else:
        dataset_id = getattr(run, "default_dataset_id", None)
    if not dataset_id:
        logger.error("Actor run finished but returned no dataset ID. Aborting.")
        sys.exit(1)

    logger.info("Actor run finished. Fetching dataset items (id=%s)...", dataset_id)

    try:
        items = list(client.dataset(dataset_id).iterate_items())
    except ApifyApiError as e:
        logger.error("Apify API error while fetching dataset: %s", e)
        sys.exit(1)

    logger.info("Retrieved %d raw items from the actor.", len(items))
    return items


# ----------------------------------------------------------------------------
# 4. FIELD MAPPING / EXTRACTION
# ----------------------------------------------------------------------------
def detect_media_type(item: Dict[str, Any]) -> str:
    """
    Infers a simplified media type (Text, Image, Video, Link) from the
    raw actor output, which stores richer nested attachment data.
    """
    attachments = item.get("attachments") or item.get("media") or []
    if not attachments:
        # Some actor versions expose a single top-level 'type'/'mediaType' field
        top_level_type = (item.get("mediaType") or item.get("type") or "").lower()
        if "video" in top_level_type:
            return "Video"
        if "photo" in top_level_type or "image" in top_level_type:
            return "Image"
        if "link" in top_level_type or item.get("link"):
            return "Link"
        return "Text"

    # attachments can be a list of dicts with a 'type' key
    types_found = set()
    for att in attachments:
        att_type = str(att.get("type", "")).lower()
        if "video" in att_type:
            types_found.add("Video")
        elif "photo" in att_type or "image" in att_type:
            types_found.add("Image")
        elif "link" in att_type or "share" in att_type:
            types_found.add("Link")

    if "Video" in types_found:
        return "Video"
    if "Image" in types_found:
        return "Image"
    if "Link" in types_found:
        return "Link"
    return "Text"


def extract_fields(raw_items: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Maps raw Apify actor JSON output to the exact fields required for
    the academic analysis. Field names below cover the common key
    variants seen across recent versions of the Facebook Posts Scraper
    actor, since Apify actors occasionally rename fields between updates.
    """
    records = []
    for item in raw_items:
        post_text = item.get("text") or item.get("message") or ""
        post_time = item.get("time") or item.get("date") or item.get("timestamp")
        post_url = item.get("url") or item.get("postUrl") or item.get("topLevelUrl")

        likes = (
            item.get("likes")
            or item.get("likesCount")
            or item.get("reactionsCount")
            or (item.get("reactions", {}) if isinstance(item.get("reactions"), dict) else {}).get("count")
        )
        comments = item.get("comments") or item.get("commentsCount")
        shares = item.get("shares") or item.get("sharesCount")

        records.append(
            {
                "Post Text": post_text,
                "Publication Date & Time": post_time,
                "Post URL": post_url,
                "Likes/Reactions": likes,
                "Comments": comments,
                "Shares": shares,
                "Media Type": detect_media_type(item),
            }
        )

    df = pd.DataFrame(records)
    logger.info("Mapped %d records into structured DataFrame.", len(df))
    return df


# ----------------------------------------------------------------------------
# 5. DATE FILTERING (STRICT — May, June, July 2026 only)
# ----------------------------------------------------------------------------
def filter_by_date_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parses the 'Publication Date & Time' column into real datetimes and
    strictly keeps only rows within DATE_START..DATE_END inclusive.
    This is the authoritative filter — it does not rely on the actor's
    own (looser) date parameter.
    """
    if df.empty:
        logger.warning("DataFrame is empty before date filtering.")
        return df

    import datetime
    
    parsed_dates = []
    for dt_str in df["Publication Date & Time"]:
        try:
            # Apify returns ISO string like '2026-06-12T14:30:00.000Z'
            # Convert to naive string for openpyxl, just stripping Z
            d_obj = datetime.datetime.fromisoformat(str(dt_str).replace('Z', '+00:00'))
            parsed_dates.append(d_obj.date())
        except Exception:
            parsed_dates.append(None)

    before = len(df)
    
    mask = [
        (d is not None and DATE_START <= d <= DATE_END)
        for d in parsed_dates
    ]
    df_filtered = df.loc[mask].copy()
    after = len(df_filtered)

    logger.info(
        "Date filter applied: %d -> %d posts kept (window: %s to %s).",
        before, after, DATE_START, DATE_END,
    )

    # Drop any rows where the date failed to parse entirely (NaT) even
    # though they may have slipped through — extra safety net.
    df_filtered = df_filtered.dropna(subset=["Publication Date & Time"])

    return df_filtered.sort_values("Publication Date & Time").reset_index(drop=True)


# ----------------------------------------------------------------------------
# 6. CLEANING
# ----------------------------------------------------------------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills missing numeric engagement counts with 0 and missing text/media
    fields with sensible placeholders, per project requirements.
    """
    if df.empty:
        return df

    numeric_cols = ["Likes/Reactions", "Comments", "Shares"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["Post Text"] = df["Post Text"].fillna("").astype(str)
    df["Post URL"] = df["Post URL"].fillna("")
    df["Media Type"] = df["Media Type"].fillna("Text")

    # Make the datetime column Excel-friendly (Excel can't store tz-aware
    # datetimes), then convert to plain naive local-format strings.
    pass # Removed tz_localize since datetimes are naive

    return df


# ----------------------------------------------------------------------------
# 7. EXPORT TO EXCEL
# ----------------------------------------------------------------------------
def export_to_excel(df: pd.DataFrame, filename: str) -> None:
    try:
        df.to_excel(filename, index=False, engine="openpyxl")
        logger.info("Exported %d rows to '%s'.", len(df), filename)
    except Exception as e:
        logger.error("Failed to write Excel file: %s", e)
        sys.exit(1)


# ----------------------------------------------------------------------------
# 8. MAIN
# ----------------------------------------------------------------------------
def main() -> None:
    if not APIFY_API_TOKEN or APIFY_API_TOKEN == "PASTE_YOUR_APIFY_TOKEN_HERE":
        logger.error(
            "No valid Apify API token found. Set APIFY_API_TOKEN as an "
            "environment variable, or paste it into the script."
        )
        sys.exit(1)

    client = ApifyClient(APIFY_API_TOKEN)

    # 1. Scrape posts
    page_url = PAGE_URL

    raw_items = run_facebook_scraper(client, page_url)
    if not raw_items:
        logger.warning("No posts were returned by the actor. Exiting.")
        sys.exit(0)

    df = extract_fields(raw_items)
    import json
    with open("raw_dump.json", "w", encoding="utf-8") as f:
        json.dump(raw_items, f, indent=2)
    try:
        df = filter_by_date_range(df)
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(f"Exception during filtering: {e}")
        sys.exit(1)

    if df.empty:
        logger.warning(
            "No posts fell within the %s to %s window. "
            "The page may not have posted during this period, or "
            "MAX_POSTS_TO_FETCH may need to be increased to reach further "
            "back/forward in the page's history.",
            DATE_START, DATE_END,
        )

    df = clean_dataframe(df)
    export_to_excel(df, OUTPUT_FILENAME)

    logger.info("Done. Final dataset shape: %s", df.shape)


if __name__ == "__main__":
    main()