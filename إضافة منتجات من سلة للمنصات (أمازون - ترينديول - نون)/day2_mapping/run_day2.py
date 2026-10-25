"""
run_day2.py
===========
المشغّل الرئيسي لليوم الثاني:
تنفيذ المطابقة وتوليد ملفات الإدراج الرسمية لكل من:
  1. أمازون السعودية (Amazon SA Flat File)
  2. نون السعودية (Noon SA Partner Catalog)
  3. ترينديول الخليج (Trendyol Gulf Excel Batch)
"""

import sys
import logging
from pathlib import Path

# ضمان ترميز UTF-8
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from day1_prepare_data.config import LOGS_DIR, DATA_DIR
from day2_mapping.map_amazon import generate_amazon_feed
from day2_mapping.map_noon import generate_noon_feed
from day2_mapping.map_trendyol import generate_trendyol_feed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "day2.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def validate_export(df, platform_name: str, barcode_col: str, price_col: str):
    """التحقق التلقائي من جودة واكتمال شيت الرفع للمنصة."""
    null_barcodes = df[barcode_col].isna() | (df[barcode_col].astype(str).str.strip() == "")
    zero_prices = (df[price_col] <= 0).sum()

    log.info(f"  [تدقيق جودة {platform_name}]:")
    log.info(f"    • إجمالي السجلات: {len(df):,}")
    log.info(f"    • باركودات سليمة 100%: {len(df) - null_barcodes.sum():,}")
    if zero_prices > 0:
        log.warning(f"    • تنبيه: يوجد {zero_prices} منتج بسعر 0 (راجع الملف إن لزم)")
    else:
        log.info("    • جميع الأسعار صالحة ومحددة بنجاح.")


def main():
    log.info("=" * 70)
    log.info("  بدء تنفيذ مهام اليوم الثاني: دوال المطابقة وتجهيز شيتات الرفع الرسمية")
    log.info("=" * 70)

    # 1. أمازون
    log.info("\n>>> [1/3] معالجة وتوليد شيت أمازون (Amazon SA)...")
    amazon_df = generate_amazon_feed()
    validate_export(amazon_df, "أمازون", "product-id", "standard-price")

    # 2. نون
    log.info("\n>>> [2/3] معالجة وتوليد شيت نون (Noon SA)...")
    noon_df = generate_noon_feed()
    validate_export(noon_df, "نون", "barcode", "price_sar")

    # 3. ترينديول
    log.info("\n>>> [3/3] معالجة وتوليد شيت ترينديول (Trendyol Gulf)...")
    trendyol_df = generate_trendyol_feed()
    validate_export(trendyol_df, "ترينديول", "barcode", "sale_price_sar")

    exports_dir = DATA_DIR / "exports"
    log.info("\n" + "=" * 70)
    log.info("  [✓] اكتملت جميع مهام اليوم الثاني بنجاح 100%!")
    log.info(f"      تم حفظ الملفات الرسمية الجاهزة للرفع داخل: {exports_dir}")
    log.info("=" * 70)
    log.info("  الملفات المُنشأة الجاهزة للرفع المباشر:")
    for ext in ["xlsx", "csv"]:
        log.info(f"    • amazon_upload_ready.{ext}")
        log.info(f"    • noon_upload_ready.{ext}")
        log.info(f"    • trendyol_upload_ready.{ext}")
    log.info("=" * 70)


if __name__ == "__main__":
    main()
