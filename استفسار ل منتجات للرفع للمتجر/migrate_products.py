#!/usr/bin/env python3
"""
Product Data Migration Script
==============================
Cleans HTML product descriptions, extracts embedded size/measurement-chart
images, OCRs them (Arabic + English), and writes a new Excel file ready for
store upload.

-----------------------------------------------------------------------------
SETUP (run once)
-----------------------------------------------------------------------------
1. Install Tesseract OCR (the engine itself, not just the python wrapper):

   Ubuntu/Debian:
       sudo apt-get update
       sudo apt-get install -y tesseract-ocr tesseract-ocr-ara tesseract-ocr-eng

   macOS (Homebrew):
       brew install tesseract tesseract-lang

   Windows:
       Download installer from https://github.com/UB-Mannheim/tesseract/wiki
       (make sure to tick the Arabic language pack during install), then add
       the install folder to your PATH.

2. Install the Python dependencies:

       pip install pandas openpyxl beautifulsoup4 lxml pillow pytesseract requests tqdm ftfy

3. Confirm Tesseract is reachable:

       tesseract --list-langs
       # should list both "ara" and "eng"

-----------------------------------------------------------------------------
USAGE
-----------------------------------------------------------------------------
    python migrate_products.py ^
        --input "Testing_.xlsx" ^
        --txt "Product_desc.txt" ^
        --output "products_clean.xlsx" ^
        --image-cache "./image_cache"

Run `python migrate_products.py --help` for all options.
"""

#!/usr/bin/env python3
"""
Product Data Migration Script (Hybrid: HTML Tables + Image OCR)
===============================================================
"""

import argparse
import csv
import io
import json
import os
import re
import sys
from collections import defaultdict
from hashlib import md5

import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x

try:
    import ftfy
except ImportError:
    ftfy = None


def fix_mojibake(text: str) -> str:
    if not text:
        return text
    if ftfy is not None:
        return ftfy.fix_text(text)
    try:
        return text.encode("cp1252", errors="strict").decode("utf-8", errors="strict")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text  


def load_table(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, engine="openpyxl")
        if df.shape[1] > 1:
            return df
    except Exception:
        pass

    with open(path, encoding="utf-8", errors="replace") as f:
        sample = f.read(4096)
    delimiter = "\t" if sample.count("\t") > sample.count(",") else ","

    df = pd.read_csv(
        path,
        sep=delimiter,
        encoding="utf-8",
        engine="python",
        on_bad_lines="warn",
        dtype=str,
        keep_default_na=False,
    )
    return df


def fix_malformed_src(html: str) -> str:
    return re.sub(r'(?<!src=")src(https?://)', r'src="\1', html)


def extract_and_clean_html(html: str) -> tuple:
    """
    MODIFIED: Extracts HTML tables FIRST, then cleans the description.
    Returns: (cleaned_text_string, list_of_extracted_tables)
    """
    if not html or not str(html).strip():
        return "", []

    html = str(html)
    html = fix_mojibake(html)
    html = fix_malformed_src(html).replace('""', '"')

    soup = BeautifulSoup(html, "lxml")

    # 1. Extract HTML tables before decomposing them
    extracted_html_tables = []
    for table in soup.find_all("table"):
        table_rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            if any(cells):  # skip empty rows
                table_rows.append(cells)
        if table_rows:
            extracted_html_tables.append(table_rows)

    # 2. Drop tags (Added 'details' and 'summary' to remove junk)
    for tag in soup(["script", "style", "img", "table", "iframe", "meta", "link", "details", "summary"]):
        tag.decompose()

    # 3. Clean remaining text
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for block in soup.find_all(["p", "div", "li", "tr", "h1", "h2", "h3", "h4"]):
        block.append("\n")

    text = soup.get_text()

    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    
    deduped = []
    for ln in lines:
        if not deduped or deduped[-1] != ln:
            deduped.append(ln)

    return "\n".join(deduped).strip(), extracted_html_tables


def extract_image_urls(html: str) -> list:
    if not html or not str(html).strip():
        return []
    html = fix_malformed_src(str(html)).replace('""', '"')
    soup = BeautifulSoup(html, "lxml")
    urls = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and src.startswith("http"):
            urls.append(src.strip())
    seen = set()
    ordered_unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered_unique.append(u)
    return ordered_unique


class ImageOCRCache:
    def __init__(self, cache_dir: str, langs: str = "ara+eng", timeout: int = 20):
        self.cache_dir = cache_dir
        self.langs = langs
        self.timeout = timeout
        os.makedirs(cache_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (ProductMigrationBot)"})
        self._mem_cache = {}

    def _cache_path(self, url: str) -> str:
        key = md5(url.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{key}.json")

    def get_table(self, url: str) -> dict:
        if url in self._mem_cache:
            return self._mem_cache[url]

        cache_file = self._cache_path(url)
        if os.path.exists(cache_file):
            with open(cache_file, encoding="utf-8") as f:
                result = json.load(f)
            self._mem_cache[url] = result
            return result

        result = self._download_and_ocr(url)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        self._mem_cache[url] = result
        return result

    def _download_and_ocr(self, url: str) -> dict:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        except Exception as e:
            return {"rows": [], "raw_text": "", "error": f"download_failed: {e}"}

        if pytesseract is None:
            return {"rows": [], "raw_text": "", "error": "pytesseract_not_installed"}

        try:
            return ocr_image_to_rows(image, self.langs)
        except Exception as e:
            return {"rows": [], "raw_text": "", "error": f"ocr_failed: {e}"}


def ocr_image_to_rows(image: Image.Image, langs: str = "ara+eng") -> dict:
    raw_text = pytesseract.image_to_string(image, lang=langs).strip()
    data = pytesseract.image_to_data(image, lang=langs, output_type=pytesseract.Output.DICT)

    words = []
    n = len(data["text"])
    for i in range(n):
        txt = data["text"][i].strip()
        if not txt:
            continue
        conf = float(data.get("conf", ["-1"] * n)[i] or -1)
        if conf != -1 and conf < 30:
            continue  
        words.append({
            "text": txt, "left": data["left"][i], "top": data["top"][i],
            "width": data["width"][i], "height": data["height"][i],
        })

    if not words:
        return {"rows": [], "raw_text": raw_text}

    words.sort(key=lambda w: w["top"])
    row_tol = max(10, int(sum(w["height"] for w in words) / len(words) * 0.6))
    rows = []
    current_row = [words[0]]
    current_center = words[0]["top"] + words[0]["height"] / 2

    for w in words[1:]:
        center = w["top"] + w["height"] / 2
        if abs(center - current_center) <= row_tol:
            current_row.append(w)
            current_center = sum(x["top"] + x["height"] / 2 for x in current_row) / len(current_row)
        else:
            rows.append(current_row)
            current_row = [w]
            current_center = center
    rows.append(current_row)

    centers = sorted(w["left"] + w["width"] / 2 for w in words)
    col_tol = max(20, int(sum(w["width"] for w in words) / len(words)))
    col_bins = []
    for c in centers:
        if not col_bins or c - col_bins[-1][-1] > col_tol:
            col_bins.append([c])
        else:
            col_bins[-1].append(c)
    col_centers = [sum(b) / len(b) for b in col_bins]

    def nearest_col(x_center):
        return min(range(len(col_centers)), key=lambda i: abs(col_centers[i] - x_center))

    structured_rows = []
    for row in rows:
        row.sort(key=lambda w: w["left"])
        cells = defaultdict(list)
        for w in row:
            col_idx = nearest_col(w["left"] + w["width"] / 2)
            cells[col_idx].append(w["text"])
        max_col = max(cells.keys()) if cells else 0
        row_out = [" ".join(cells.get(i, [])).strip() for i in range(max_col + 1)]
        if any(row_out):
            structured_rows.append(row_out)

    return {"rows": structured_rows, "raw_text": raw_text}


def merge_table_results(table_results: list) -> dict:
    all_rows = []
    errors = []
    for res in table_results:
        if res.get("error"):
            errors.append(res["error"])
        if res.get("rows"):
            all_rows.extend(res["rows"])
    return {"rows": all_rows, "errors": errors}


def process_dataframe(df: pd.DataFrame, ocr_cache: ImageOCRCache, desc_columns: list, limit: int = None) -> tuple:
    out_rows = []
    size_table_rows = []
    max_cols_seen = 0

    total = len(df) if limit is None else min(limit, len(df))
    df_iter = df.head(limit) if limit is not None else df

    for _, row in tqdm(df_iter.iterrows(), total=total, desc="Processing products"):
        new_row = row.to_dict()
        sku = str(row.get("sku", row.get("barcode", "")))

        for col in desc_columns:
            if col not in df.columns:
                continue
            html_val = row.get(col, "")

            # 1. Clean HTML and extract actual HTML tables
            cleaned_text, html_tables = extract_and_clean_html(html_val)
            new_row[f"{col}_clean"] = cleaned_text

            # 2. Find images and run OCR
            image_urls = extract_image_urls(html_val)
            table_results = [ocr_cache.get_table(u) for u in image_urls]
            merged_ocr = merge_table_results(table_results)

            # 3. Combine HTML tables with OCR tables!
            all_table_rows = []
            for ht in html_tables:
                all_table_rows.extend(ht)
            if merged_ocr["rows"]:
                all_table_rows.extend(merged_ocr["rows"])

            # Save human-readable flat version
            flat_rows_text = "\n".join(" | ".join(r) for r in all_table_rows)
            new_row[f"{col}_size_table_text"] = flat_rows_text

            # Save long-format details
            for r_idx, r in enumerate(all_table_rows):
                size_table_rows.append({
                    "sku": sku,
                    "source_column": col,
                    "row_index": r_idx,
                    "cells": r,
                })
                max_cols_seen = max(max_cols_seen, len(r))

            if merged_ocr["errors"]:
                new_row[f"{col}_ocr_notes"] = "; ".join(merged_ocr["errors"])

        out_rows.append(new_row)

    products_df = pd.DataFrame(out_rows)

    expanded = []
    for entry in size_table_rows:
        record = {
            "sku": entry["sku"],
            "source_column": entry["source_column"],
            "row_index": entry["row_index"],
        }
        for i in range(max_cols_seen):
            record[f"col_{i + 1}"] = entry["cells"][i] if i < len(entry["cells"]) else ""
        expanded.append(record)
    size_tables_df = pd.DataFrame(expanded)

    return products_df, size_tables_df


def write_output(products_df: pd.DataFrame, size_tables_df: pd.DataFrame, output_path: str):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        products_df.to_excel(writer, sheet_name="Products", index=False)
        if not size_tables_df.empty:
            size_tables_df.to_excel(writer, sheet_name="Size_Tables", index=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="products_clean.xlsx")
    parser.add_argument("--image-cache", default="./image_cache")
    parser.add_argument("--desc-columns", nargs="*", default=["description_en", "description_ar", "Description"])
    parser.add_argument("--langs", default="ara+eng")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    df = load_table(args.input)
    ocr_cache = ImageOCRCache(args.image_cache, langs=args.langs)
    
    products_df, size_tables_df = process_dataframe(
        df, ocr_cache, desc_columns=args.desc_columns, limit=args.limit
    )

    write_output(products_df, size_tables_df, args.output)
    print("Done!")

if __name__ == "__main__":
    main()