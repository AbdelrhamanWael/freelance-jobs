"""
map_trendyol.py
===============
توليد شيت إدراج منتجات ترينديول الخليج (Trendyol Gulf Excel Batch Sheet)
وفق مواصفات بوابة بائعي ترينديول.
"""

import sys
from pathlib import Path

# ضمان ترميز UTF-8
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import logging
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from day1_prepare_data.config import CLEAN_DIR, LOGS_DIR, DATA_DIR
from day2_mapping.category_dictionary import match_category
from day2_mapping.content_generator import (
    strip_html, generate_standard_title, calculate_platform_price
)

log = logging.getLogger(__name__)


def generate_trendyol_feed() -> pd.DataFrame:
    """تحويل بيانات trendyol_ready إلى شيت الإدراج الرسمي لترينديول."""
    input_path = CLEAN_DIR / "trendyol_ready.pkl"
    if not input_path.exists():
        log.error(f"الملف {input_path} غير موجود. قم بتشغيل اليوم الأول أولاً.")
        sys.exit(1)

    df_in = pd.read_pickle(input_path)
    log.info(f"جاري تحويل {len(df_in):,} منتج إلى قالب ترينديول الرسمي...")

    rows = []
    for _, row in df_in.iterrows():
        name_ar = str(row.get("name_ar", "")).strip()
        category = str(row.get("category", "")).strip()
        brand = str(row.get("brand", "")).strip() or "قطاف الطبيعة"
        weight_kg = float(row.get("weight_kg", 0.5))
        barcode = str(row.get("barcode", "")).strip()
        sku = str(row.get("sku", "")).strip()
        base_price = float(row.get("price", 0.0))
        sale_price = float(row.get("sale_price", 0.0))
        quantity = int(row.get("quantity", 0))

        # مطابقة التصنيف
        cat_info = match_category(category, name_ar, "trendyol")

        # توليد المحتوى
        title = generate_standard_title(brand, name_ar, weight_kg)
        desc_clean = strip_html(str(row.get("description", "")))
        final_price = calculate_platform_price(base_price)
        # السعر المقترح الأصلي (List Price) قبل الخصم
        list_price = round(final_price * 1.15, 2) if final_price > 0 else 0.0

        record = {
            "barcode"                : barcode,
            "model_code"             : sku,
            "brand_name"             : brand,
            "category_id"            : cat_info.get("category_id", "103850"),
            "category_name"          : cat_info.get("category_name", "Süpermarket"),
            "product_title"          : title,
            "sale_price_sar"         : final_price,
            "list_price_sar"         : list_price,
            "stock_quantity"         : quantity,
            "product_description"    : desc_clean[:2500],
            "image_url"              : str(row.get("images", "")),
            "delivery_duration_days" : 3,
            "cargo_company"          : "SMSA Express",
            "vat_rate_percent"       : 15,
            "origin_country"         : "SA",
            "item_weight_kg"         : weight_kg,
        }
        rows.append(record)

    df_out = pd.DataFrame(rows)

    exports_dir = DATA_DIR / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = exports_dir / "trendyol_upload_ready.csv"
    xlsx_path = exports_dir / "trendyol_upload_ready.xlsx"

    df_out.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df_out.to_excel(xlsx_path, index=False, engine="openpyxl")

    log.info(f"✓ تم توليد ملف إدراج ترينديول بنجاح: {xlsx_path.name} ({len(df_out)} منتج)")
    return df_out


if __name__ == "__main__":
    generate_trendyol_feed()
