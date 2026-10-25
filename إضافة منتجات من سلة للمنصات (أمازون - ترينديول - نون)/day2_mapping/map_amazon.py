"""
map_amazon.py
=============
توليد شيت إدراج منتجات أمازون السعودية (Amazon SA Flat File / Inventory Feed)
وفق مواصفات وقوالب أمازون الرسمية المعتمدة في Seller Central.
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
    calculate_platform_price, generate_search_terms, generate_amazon_highlight
)

log = logging.getLogger(__name__)


def generate_amazon_feed() -> pd.DataFrame:
    """تحويل بيانات amazon_ready إلى شيت الإدراج الرسمي لأمازون بالأعمدة المعيارية المعتمدة."""
    input_path = CLEAN_DIR / "amazon_ready.pkl"
    if not input_path.exists():
        log.error(f"الملف {input_path} غير موجود. قم بتشغيل اليوم الأول أولاً.")
        sys.exit(1)

    df_in = pd.read_pickle(input_path)

    # 1. إزالة التكرار في الـ SKU لضمان عدم رفض أي سطر
    df_in = df_in.drop_duplicates(subset=["sku"], keep="first")

    # 2. توريث الصور للمتغيرات (Variants) من المنتج الأب
    df_in["images"] = df_in.groupby("name_ar")["images"].transform(lambda g: g.ffill().bfill())

    # 3. توريث الماركة للمتغيرات وضبط الافتراضي على "قطاف الطبيعة"
    df_in["brand"] = df_in.groupby("name_ar")["brand"].transform(lambda g: g.ffill().bfill())
    df_in["brand"] = df_in["brand"].fillna("قطاف الطبيعة").replace({"nan": "قطاف الطبيعة", "": "قطاف الطبيعة"})

    log.info(f"جاري تحويل {len(df_in):,} منتج إلى قالب أمازون المتوافق بالكامل...")

    rows = []
    for _, row in df_in.iterrows():
        name_ar = str(row.get("name_ar", "")).strip()
        category = str(row.get("category", "")).strip()
        raw_brand = str(row.get("brand", "")).strip()
        brand = "قطاف الطبيعة" if raw_brand in ("", "nan", "None") else raw_brand
        weight_kg = float(row.get("weight_kg", 0.5))
        barcode = str(row.get("barcode", "")).strip()
        sku = str(row.get("sku", "")).strip()
        base_price = float(row.get("price", 0.0))
        quantity = int(row.get("quantity", 0))

        # مطابقة التصنيف
        cat_info = match_category(category, name_ar, "amazon")

        # توليد المحتوى
        title = generate_standard_title(brand, name_ar, weight_kg)
        desc_clean = strip_html(str(row.get("description", "")))
        if not desc_clean or len(desc_clean.strip()) < 5:
            desc_clean = f"منتج {name_ar} طبيعي عالي الجودة من علامة {brand}، معبأ ومغلف بعناية فائقة لضمان أعلى معايير النقاء والجودة."
        bullets = extract_bullet_points(row.to_dict())
        final_price = calculate_platform_price(base_price)
        keywords = generate_search_terms(name_ar, category, brand)
        highlight = generate_amazon_highlight(name_ar, category)

        # تحديد نوع الباركود (EAN إذا كان 13 رقماً، UPC إذا كان 12)
        id_type = "EAN" if len(barcode) == 13 else ("UPC" if len(barcode) == 12 else "EAN")

        # تحديد معايير السلامة والتحذيرات بحسب نوع المنتج
        is_beauty = cat_info.get("product_type") == "BEAUTY"
        safety_warn = "For external use only." if is_beauty else "Store in a cool and dry place."
        unit_count_val = int(weight_kg * 1000) if weight_kg < 5.0 else int(weight_kg)
        unit_type_val = "Gram" if weight_kg < 5.0 else "Kilogram"

        # الأعمدة بالأسماء الإنجليزية القياسية المعتمدة لدى نظام مسودات ورفع أمازون (Non-Amazon File)
        # تشمل متطلبات أقسام العطارة والأغذية الإلزامية (الموديل، درجة الحرارة، المكونات، الصلاحية)
        record = {
            "SKU"                           : sku,
            "External Product ID"           : barcode,
            "External Product ID Type"      : id_type,
            "Has GTIN exemption?"           : "No",
            "Product Type"                  : cat_info.get("product_type", "GROCERY"),
            "Item Name"                     : title,
            "Brand Name"                    : brand,
            "Model Number"                  : sku,
            "Part Number"                   : sku,
            "Number of Items"               : 1,
            "Temperature Rating"            : "Ambient",
            "Ingredients"                   : name_ar,
            "Allergen Information"          : "Allergen-Free",
            "Product Expiration Type"       : "Expiration Date Required",
            "FC Shelf Life"                 : 365,
            "FC Shelf Life Unit"            : "Days",
            "Standard Price"                : final_price,
            "List Price With Tax"           : final_price,
            "Currency"                      : "SAR",
            "Quantity"                      : quantity,
            "Item Condition"                : "New",
            "Main Image URL"                : str(row.get("images", "")),
            "Product Description"           : desc_clean[:2000],
            "Bullet Point 1"                : bullets[0],
            "Bullet Point 2"                : bullets[1],
            "Bullet Point 3"                : bullets[2],
            "Bullet Point 4"                : bullets[3],
            "Bullet Point 5"                : bullets[4],
            "Country of Origin"             : "Saudi Arabia",
            "Dangerous Goods Regulations"   : "Not Applicable",
            "Safety Warning"                : safety_warn,
            "Unit Count"                    : unit_count_val,
            "Unit Count Type"               : unit_type_val,
            "Item Weight"                   : weight_kg,
            "Item Weight Unit of Measure"   : "KG",
            "Recommended Browse Nodes"      : cat_info.get("browse_node", "16402344031"),
            "Item Type Keyword"             : cat_info.get("item_type", "pantry-staples"),
            "Generic Keywords"              : keywords[:250],
            "Fulfillment Channel"           : "DEFAULT",
            "Merchant Shipping Group Name"  : "Default Shipping",
        }
        rows.append(record)

    df_out = pd.DataFrame(rows)

    # حفظ الملفات في data/exports/
    exports_dir = DATA_DIR / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    full_dir = exports_dir / "full_catalog_290"
    full_dir.mkdir(parents=True, exist_ok=True)

    # حفظ النسخ الرئيسية
    for target_dir in [exports_dir, full_dir]:
        df_out.to_csv(target_dir / "amazon_upload_ready.csv", index=False, encoding="utf-8-sig")
        df_out.to_excel(target_dir / "amazon_upload_ready.xlsx", index=False, engine="openpyxl")

    # حفظ ملف إضافي باسم واضح وصريح للمستخدم
    named_xlsx = exports_dir / "amazon_upload_ready_290_products.xlsx"
    df_out.to_excel(named_xlsx, index=False, engine="openpyxl")

    log.info(f"✓ تم توليد ملف إدراج أمازون الكامل بنجاح: {named_xlsx.name} ({len(df_out)} منتج)")
    return df_out


if __name__ == "__main__":
    generate_amazon_feed()
