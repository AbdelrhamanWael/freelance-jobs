"""
step3_split_platforms.py
========================
الخطوة الثالثة: التقسيم المبدئي للبيانات النظيفة إلى ثلاثة DataFrames مستقلة:
  - نسخة لأمازون (Amazon)
  - نسخة لنون (Noon)
  - نسخة لترينديول (Trendyol)

كل DataFrame يحتوي على البيانات المشتركة بالإضافة إلى الأعمدة المخصصة
لكل منصة جاهزة لاستقبال دوال المطابقة (Mapping) في اليوم الثاني.
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
from day1_prepare_data.config import CLEAN_DIR, LOGS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "day1.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── تعريف أعمدة وقوالب كل منصة لليوم الثاني ──────────────────────────────
PLATFORMS_CONFIG = {
    "amazon": {
        "display_name": "أمازون (Amazon SA)",
        "extra_columns": {
            "amazon_sku"                 : "",
            "amazon_product_id"         : "",  # EAN or UPC
            "amazon_id_type"            : "EAN",
            "amazon_browse_node"        : "",
            "amazon_bullet_1"           : "",
            "amazon_bullet_2"           : "",
            "amazon_bullet_3"           : "",
            "amazon_bullet_4"           : "",
            "amazon_bullet_5"           : "",
            "amazon_search_terms"       : "",
            "amazon_fulfillment"        : "MFN",  # Merchant Fulfilled Network
            "mapping_status"            : "pending_day2",
        }
    },
    "noon": {
        "display_name": "نون (Noon SA)",
        "extra_columns": {
            "noon_partner_sku"          : "",
            "noon_barcode"              : "",
            "noon_family_code"          : "",
            "noon_category_id"          : "",
            "noon_brand_name"           : "",
            "noon_country_of_origin"    : "SA",
            "noon_warranty"             : "No Warranty",
            "mapping_status"            : "pending_day2",
        }
    },
    "trendyol": {
        "display_name": "ترينديول (Trendyol Gulf)",
        "extra_columns": {
            "trendyol_barcode"          : "",
            "trendyol_model_code"       : "",
            "trendyol_category_id"      : "",
            "trendyol_brand_id"         : "",
            "trendyol_cargo_company_id" : "",
            "trendyol_delivery_duration": "3",
            "mapping_status"            : "pending_day2",
        }
    },
}


def load_clean_data() -> pd.DataFrame:
    clean_path = CLEAN_DIR / "salla_active_products.pkl"
    if not clean_path.exists():
        log.error(f"الملف {clean_path} غير موجود. قم بتشغيل step2 أولاً.")
        sys.exit(1)
    return pd.read_pickle(clean_path)


def build_platform_dataframe(base_df: pd.DataFrame, platform_key: str) -> pd.DataFrame:
    """إنشاء نسخة مخصصة للمنصة مع دمج حقول المطابقة الخاصة بها."""
    cfg = PLATFORMS_CONFIG[platform_key]
    df = base_df.copy()

    # ربط مبدئي للـ SKU والباركود لكل منصة
    if platform_key == "amazon":
        df["amazon_sku"] = df["sku"]
        df["amazon_product_id"] = df["barcode"]
    elif platform_key == "noon":
        df["noon_partner_sku"] = df["sku"]
        df["noon_barcode"] = df["barcode"]
        df["noon_brand_name"] = df["brand"]
    elif platform_key == "trendyol":
        df["trendyol_barcode"] = df["barcode"]
        df["trendyol_model_code"] = df["sku"]

    # إضافة باقي الأعمدة المخصصة
    for col, default_val in cfg["extra_columns"].items():
        if col not in df.columns:
            df[col] = default_val

    return df


def split_and_export(base_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """تصدير ملفات كل منصة بصيغتي Pickle و CSV."""
    created_dfs = {}

    log.info("=" * 65)
    log.info("بدء تقسيم وتصدير الـ DataFrames الخاصة بالمنصات...")
    log.info("=" * 65)

    for platform_key, cfg in PLATFORMS_CONFIG.items():
        platform_df = build_platform_dataframe(base_df, platform_key)

        pkl_path = CLEAN_DIR / f"{platform_key}_ready.pkl"
        csv_path = CLEAN_DIR / f"{platform_key}_ready.csv"

        platform_df.to_pickle(pkl_path)
        platform_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        created_dfs[platform_key] = platform_df
        log.info(
            f"✓ [{cfg['display_name']:<22}] "
            f"المنتجات: {len(platform_df):>4,} | الأعمدة: {platform_df.shape[1]:>2} | "
            f"الملف: {csv_path.name}"
        )

    return created_dfs


def display_final_report(dfs: dict[str, pd.DataFrame]) -> None:
    """طباعة تقرير الإنجاز النهائي لليوم الأول."""
    log.info("")
    log.info("=" * 65)
    log.info("  ملخص اليوم الأول — تم تجهيز وتقسيم البيانات بنجاح تام")
    log.info("=" * 65)
    for p_key, p_df in dfs.items():
        disp = PLATFORMS_CONFIG[p_key]["display_name"]
        sample_sku = p_df["sku"].iloc[0] if not p_df.empty else "—"
        log.info(f"  • {disp:<24}: {len(p_df):,} منتج نشط (عينة SKU: {sample_sku})")
    log.info("-" * 65)
    log.info("  الملفات محفوظة داخل مجلد: data/clean/")
    log.info("  أنت الآن جاهز بنسبة 100% لبدء دوال المطابقة (Mapping) في اليوم الثاني!")
    log.info("=" * 65)


if __name__ == "__main__":
    clean_df = load_clean_data()
    platform_dfs = split_and_export(clean_df)
    display_final_report(platform_dfs)
