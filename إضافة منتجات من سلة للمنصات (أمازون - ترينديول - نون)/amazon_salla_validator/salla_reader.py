"""
Salla Excel / CSV Adaptive Reader.
Extracts normalized product records from Salla export files with dynamic header
detection, alias matching, and HTML cleanup.
"""

import re
import html
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd
from bs4 import BeautifulSoup

from .config import SallaProduct


# Column name aliases for multilingual / multi-format Salla exports
COLUMN_ALIASES: Dict[str, List[str]] = {
    "sku": [
        "رمز المنتج sku", "رمز المنتج", "رمز sku", "sku", "product sku",
        "كود المنتج", "sku code", "amazon_sku"
    ],
    "asin": [
        "asin", "amazon asin", "رمز asin", "amazon_asin", "amazon_product_id", "external product id"
    ],
    "name": [
        "أسم المنتج", "اسم المنتج", "اسم المنتج بالعربي", "product name",
        "name", "title", "item name", "name_ar"
    ],
    "price": [
        "سعر المنتج", "السعر", "price", "standard price", "سعر البيع",
        "regular price", "your price"
    ],
    "sale_price": [
        "السعر المخفض", "سعر التخفيض", "sale price", "discount price"
    ],
    "barcode": [
        "الباركود", "barcode", "gtin", "ean", "upc", "gtin13", "mpn"
    ],
    "description": [
        "الوصف", "وصف المنتج", "description", "product description",
        "تفاصيل المنتج", "body html"
    ],
    "category": [
        "تصنيف المنتج", "الأقسام", "القسم", "category", "categories"
    ],
    "brand": [
        "الماركة", "العلامة التجارية", "brand", "brand name"
    ],
    "weight": [
        "الوزن", "weight", "item weight", "weight_kg"
    ],
    "weight_unit": [
        "وحدة الوزن", "weight unit", "unit"
    ],
    "status": [
        "حالة المنتج", "status", "الحالة"
    ],
    "main_image": [
        "صورة المنتج", "الصور", "رابط الصورة", "image", "images",
        "main image", "image url", "product image", "main image url"
    ],
}


def clean_html_text(raw_html: Any) -> Tuple[str, List[str]]:
    """
    Strips HTML tags, extracts formatted text and distinct bullet points.
    Returns (cleaned_text, bullet_points).
    """
    if pd.isna(raw_html) or not raw_html:
        return "", []

    text_val = str(raw_html).strip()
    if not text_val or text_val.lower() == "nan":
        return "", []

    # If it doesn't look like HTML, return direct text
    if "<" not in text_val and ">" not in text_val:
        lines = [l.strip() for l in text_val.split("\n") if l.strip()]
        return text_val, lines[:5]

    soup = BeautifulSoup(text_val, "html.parser")

    # Extract bullet points from <li> elements
    bullets = []
    for li in soup.find_all("li"):
        b_text = li.get_text(strip=True)
        if b_text and len(b_text) > 3:
            bullets.append(b_text)

    # Get cleaned text
    # Replace <br> and <p> with newlines for readability
    for br in soup.find_all(["br", "p"]):
        br.replace_with(f"\n{br.get_text()}\n")

    cleaned = soup.get_text(separator=" ")
    cleaned = html.unescape(cleaned)
    # Remove redundant whitespace
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n+", "\n", cleaned).strip()

    # If no <li> found, try to extract lines as bullets
    if not bullets and cleaned:
        candidates = [line.strip("- •* ") for line in cleaned.split("\n") if len(line.strip()) > 10]
        bullets = candidates[:5]

    return cleaned, bullets


def normalize_sku(val: Any) -> str:
    """Formats SKU cleanly, avoiding scientific notation and trailing .0."""
    if pd.isna(val) or val is None:
        return ""
    if isinstance(val, float):
        if val.is_integer():
            return str(int(val))
        return f"{val:.0f}"
    val_str = str(val).strip()
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
    return val_str


def normalize_price(val: Any) -> float:
    """Extracts numeric price value from string, int, or float, handling currency symbols and abbreviations."""
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", val_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return 0.0


class SallaExcelReader:
    """Reads and parses Salla product catalog exports."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    def detect_header_and_load(self) -> pd.DataFrame:
        """
        Dynamically detects the header row by scanning the first 5 rows
        for known Salla/catalog column indicators.
        """
        suffix = self.file_path.suffix.lower()

        if suffix in [".xlsx", ".xlsm", ".xls"]:
            # Try reading first 5 rows without headers
            df_preview = pd.read_excel(self.file_path, header=None, nrows=6)
        elif suffix in [".csv", ".tsv"]:
            sep = "\t" if suffix == ".tsv" else ","
            df_preview = pd.read_csv(self.file_path, header=None, nrows=6, sep=sep)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

        detected_header_row = 0
        max_matched_aliases = 0

        # Scan each candidate row
        for row_idx in range(min(6, len(df_preview))):
            row_values = [str(x).strip().lower() for x in df_preview.iloc[row_idx].values if pd.notna(x)]
            matches = 0
            for alias_list in COLUMN_ALIASES.values():
                for alias in alias_list:
                    if any(alias in val for val in row_values):
                        matches += 1
                        break
            if matches > max_matched_aliases:
                max_matched_aliases = matches
                detected_header_row = row_idx

        # Load full DataFrame using detected header row
        if suffix in [".xlsx", ".xlsm", ".xls"]:
            df = pd.read_excel(self.file_path, header=detected_header_row)
        else:
            sep = "\t" if suffix == ".tsv" else ","
            df = pd.read_csv(self.file_path, header=detected_header_row, sep=sep)

        return df

    def match_columns(self, df_cols: List[str]) -> Dict[str, str]:
        """
        Maps standard field names to actual DataFrame column names.
        """
        mapping = {}
        cleaned_df_cols = {col: str(col).strip().lower() for col in df_cols}

        for standard_field, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                matched_col = next(
                    (orig_col for orig_col, clean_col in cleaned_df_cols.items() if alias == clean_col),
                    None
                )
                if not matched_col:
                    # Partial match fallback
                    matched_col = next(
                        (orig_col for orig_col, clean_col in cleaned_df_cols.items() if alias in clean_col),
                        None
                    )
                if matched_col:
                    mapping[standard_field] = matched_col
                    break

        return mapping

    def extract_image_urls(self, row: pd.Series, main_image_col: Optional[str]) -> List[str]:
        """Collects main image and any variant/additional image URLs."""
        images = []
        # Main image
        if main_image_col and main_image_col in row and pd.notna(row[main_image_col]):
            url = str(row[main_image_col]).strip()
            if url and url.lower() != "nan" and url.startswith("http"):
                images.append(url)

        # Additional image columns (e.g. Salla '[1] الصورة / اللون' or comma-separated)
        for col_name, val in row.items():
            col_str = str(col_name).strip()
            if col_str == main_image_col:
                continue
            if ("صورة" in col_str or "image" in col_str.lower()) and pd.notna(val):
                v_str = str(val).strip()
                if v_str.startswith("http"):
                    if v_str not in images:
                        images.append(v_str)

        # Also handle comma-separated images in main image
        if images and "," in images[0]:
            split_urls = [u.strip() for u in images[0].split(",") if u.strip().startswith("http")]
            images = split_urls + images[1:]

        return images

    def load_products(self, limit: Optional[int] = None) -> List[SallaProduct]:
        """Loads and returns all valid Salla products as SallaProduct instances."""
        df = self.detect_header_and_load()
        col_map = self.match_columns(list(df.columns))

        sku_col = col_map.get("sku")
        name_col = col_map.get("name")
        price_col = col_map.get("price")

        if not sku_col and not name_col:
            raise ValueError(
                f"Could not identify required columns ('SKU' or 'Name') in file {self.file_path}. "
                f"Detected columns: {list(df.columns)}"
            )

        products: List[SallaProduct] = []

        for idx, row in df.iterrows():
            if limit and len(products) >= limit:
                break

            sku = normalize_sku(row.get(sku_col)) if sku_col else ""
            name = str(row.get(name_col, "")).strip() if name_col else ""

            # Ignore empty rows
            if not sku and not name:
                continue

            price = normalize_price(row.get(price_col)) if price_col else 0.0

            sale_price = None
            if col_map.get("sale_price") and pd.notna(row.get(col_map["sale_price"])):
                sale_price = normalize_price(row.get(col_map["sale_price"]))

            barcode = normalize_sku(row.get(col_map.get("barcode", ""))) if col_map.get("barcode") else None
            brand = str(row.get(col_map.get("brand", ""), "")).strip() or None
            category = str(row.get(col_map.get("category", ""), "")).strip() or None
            status = str(row.get(col_map.get("status", ""), "")).strip() or None

            # Weight
            weight = None
            if col_map.get("weight") and pd.notna(row.get(col_map["weight"])):
                try:
                    weight = float(row.get(col_map["weight"]))
                except (ValueError, TypeError):
                    weight = None
            weight_unit = str(row.get(col_map.get("weight_unit", ""), "")).strip() or None

            # Description and bullets
            desc_raw = str(row.get(col_map.get("description", ""), "")) if col_map.get("description") else ""
            desc_text, bullets = clean_html_text(desc_raw)

            # Images
            images = self.extract_image_urls(row, col_map.get("main_image"))

            raw_dict = {str(k): str(v) for k, v in row.to_dict().items() if pd.notna(v)}

            product = SallaProduct(
                sku=sku or barcode or f"ROW_{idx+1}",
                name=name,
                price=price,
                sale_price=sale_price,
                barcode=barcode,
                category=category,
                brand=brand,
                weight=weight,
                weight_unit=weight_unit,
                status=status,
                description_raw=desc_raw,
                description_text=desc_text,
                bullet_points=bullets,
                images=images,
                raw_data=raw_dict,
            )
            products.append(product)

        return products
