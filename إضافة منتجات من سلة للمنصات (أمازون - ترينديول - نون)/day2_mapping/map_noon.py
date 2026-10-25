"""
map_noon.py
===========
توليد شيت إدراج منتجات نون السعودية (Noon SA Partner Catalog Template)
وفق مواصفات بوابة بائعي نون (Noon Seller Lab).
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
    strip_html, extract_bullet_points, generate_standard_title,
    calculate_platform_price
)

log = logging.getLogger(__name__)


def generate_noon_feed() -> pd.DataFrame:
    """تحويل بيانات noon_ready إلى شيت الإدراج الرسمي لنون."""
    input_path = CLEAN_DIR / "noon_ready.pkl"
    if not input_path.exists():
        log.error(f"الملف {input_path} غير موجود. قم بتشغيل اليوم الأول أولاً.")
        sys.exit(1)

    df_in = pd.read_pickle(input_path)
    log.info(f"جاري تحويل {len(df_in):,} منتج إلى قالب نون الرسمي...")

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
        cat_info = match_category(category, name_ar, "noon")

        # توليد المحتوى
        title_ar = generate_standard_title(brand, name_ar, weight_kg)
        desc_clean = strip_html(str(row.get("description", "")))
        bullets = extract_bullet_points(row.to_dict())
        final_price = calculate_platform_price(base_price)
        final_sale_price = calculate_platform_price(sale_price) if sale_price > 0 else ""

        record = {
            "partner_sku"            : sku,
            "barcode"                : barcode,
            "product_title_ar"       : title_ar,
            "brand"                  : brand,
            "noon_category_code"     : cat_info.get("category_code", "pantry_staples_general"),
            "category_name_ar"       : cat_info.get("category_name_ar", "بقالة ومستلزمات"),
            "family_code"            : cat_info.get("family_code", "NOON_GEN") + f"_{sku[:6]}",
            "price_sar"              : final_price,
            "sale_price_sar"         : final_sale_price,
            "stock_quantity"         : quantity,
            "description_ar"         : desc_clean[:3000],
            "bullet_point_1"         : bullets[0],
            "bullet_point_2"         : bullets[1],
            "bullet_point_3"         : bullets[2],
            "bullet_point_4"         : bullets[3],
            "bullet_point_5"         : bullets[4],
            "image_url_1"            : str(row.get("images", "")),
            "weight_kg"              : weight_kg,
            "country_of_origin"      : "SA",
            "warranty_type"          : "No Warranty",
            "package_contents"       : f"عبوة واحدة من {name_ar}",
            "storage_conditions"     : "يحفظ في مكان جاف وبارد",
        }
        rows.append(record)

    df_out = pd.DataFrame(rows)

    exports_dir = DATA_DIR / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = exports_dir / "noon_upload_ready.csv"
    xlsx_path = exports_dir / "noon_upload_ready.xlsx"

    df_out.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df_out.to_excel(xlsx_path, index=False, engine="openpyxl")

    log.info(f"✓ تم توليد ملف إدراج نون بنجاح: {xlsx_path.name} ({len(df_out)} منتج)")
    return df_out


if __name__ == "__main__":
    generate_noon_feed()
