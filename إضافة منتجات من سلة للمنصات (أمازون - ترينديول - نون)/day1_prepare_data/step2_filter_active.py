"""
step2_filter_active.py
======================
الخطوة الثانية: الفلترة الشرطية وتنظيف البيانات:
  1. استبعاد المنتجات المخفية ("مخفي")
  2. الإبقاء على المنتجات النشطة / المتاحة ("متاح")
  3. استبعاد المنتجات التي تفتقر إلى رمز SKU / باركود وحفظها في excluded_products.csv
  4. تنظيف وتوحيد الأوزان بالكيلوجرام (weight_kg)
  5. تنظيف الأسعار والأرقام
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
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from day1_prepare_data.config import (
    ACTIVE_STATUS_VALUES, STRICT_ACTIVE_ONLY, DEFAULT_ACTIVE_STOCK,
    BASE_COLUMNS, CLEAN_DIR, LOGS_DIR
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "day1.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def load_renamed(path: Path) -> pd.DataFrame:
    if not path.exists():
        log.error(f"الملف غير موجود: {path}. قم بتشغيل step1_load_raw.py أولاً.")
        sys.exit(1)
    return pd.read_pickle(path)


def filter_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    تطبيق الفلترة الشرطية:
      - عزل المنتجات المخفية والمستبعدة
      - استبقاء المنتجات النشطة ذات الـ SKU الصالح
    """
    total_start = len(df)
    log.info(f"بدء الفلترة لإجمالي {total_start:,} سجل...")

    excluded_records = []

    # 1. فحص الحالة
    status_series = df.get("status", pd.Series(dtype=str)).fillna("").astype(str).str.strip()

    if STRICT_ACTIVE_ONLY:
        active_mask = status_series.isin(ACTIVE_STATUS_VALUES)
        hidden_or_inactive = df[~active_mask].copy()
        hidden_or_inactive["exclusion_reason"] = "حالة غير نشطة / مخفي / غير متاح (" + status_series[~active_mask] + ")"
        excluded_records.append(hidden_or_inactive)
        df_filtered = df[active_mask].copy()
    else:
        hidden_mask = status_series.str.lower().isin(["مخفي", "hidden"])
        hidden_df = df[hidden_mask].copy()
        hidden_df["exclusion_reason"] = "منتج مخفي"
        excluded_records.append(hidden_df)
        df_filtered = df[~hidden_mask].copy()

    log.info(f"المنتجات المتبقية بعد فلتر الحالة: {len(df_filtered):,} (المستبعد: {total_start - len(df_filtered):,})")

    # 2. فحص SKU والباركود
    sku_series = df_filtered.get("sku", pd.Series(dtype=str)).fillna("").astype(str).str.strip()
    no_sku_mask = (sku_series == "") | (sku_series.str.lower() == "nan")

    if no_sku_mask.sum() > 0:
        no_sku_df = df_filtered[no_sku_mask].copy()
        no_sku_df["exclusion_reason"] = "لا يحتوي على SKU / باركود"
        excluded_records.append(no_sku_df)
        df_filtered = df_filtered[~no_sku_mask].copy()
        log.info(f"تم استبعاد {len(no_sku_df)} منتج لعدم وجود SKU.")

    # تجميع ملف المستبعدات
    if excluded_records:
        df_excluded = pd.concat(excluded_records, ignore_index=True)
    else:
        df_excluded = pd.DataFrame()

    log.info(f"إجمالي المنتجات المؤهلة والمعتمدة: {len(df_filtered):,}")
    return df_filtered, df_excluded


def clean_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """تنظيف وتوحيد الأعمدة الرقمية، الأوزان، والأسعار."""
    df = df.copy()

    # تنظيف الأسعار
    for col in ["price", "sale_price", "cost_price"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
                .replace({"nan": "0", "None": "0", "": "0"})
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).round(2)

    # توحيد الوزن بالكيلوجرام (weight_kg)
    if "weight" in df.columns and "weight_unit" in df.columns:
        weights = pd.to_numeric(df["weight"].astype(str).str.replace(",", "", regex=False), errors="coerce").fillna(0.0)
        units = df["weight_unit"].astype(str).str.strip().str.lower()

        # إذا كانت الوحدة جرام (g)، نقسم على 1000
        df["weight_kg"] = np.where(units == "g", (weights / 1000.0).round(3), weights.round(3))
    elif "weight" in df.columns:
        df["weight_kg"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.5).round(3)
    else:
        df["weight_kg"] = 0.5  # قيمة افتراضية نصف كيلو

    # ملء الباركود من SKU إذا كان الباركود غير محدد
    if "barcode" in df.columns and "sku" in df.columns:
        barcode_clean = df["barcode"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).replace({"nan": "", "None": ""})
        df["barcode"] = np.where(barcode_clean != "", barcode_clean, df["sku"])
    elif "sku" in df.columns:
        df["barcode"] = df["sku"]

    # حساب كمية المخزون (Quantity):
    # المنتجات بحالة "متاح" تأخذ الكمية الافتراضية، والمنتجات "غير متاح" تأخذ 0
    is_avail = df["status"].astype(str).str.strip().isin(ACTIVE_STATUS_VALUES)
    df["quantity"] = np.where(is_avail, DEFAULT_ACTIVE_STOCK, 0)

    # ضبط الأعمدة الأساسية
    for c in BASE_COLUMNS:
        if c not in df.columns:
            df[c] = ""

    df = df[BASE_COLUMNS].copy()
    return df


if __name__ == "__main__":
    tmp_path = CLEAN_DIR / "_raw_renamed.pkl"
    raw_df = load_renamed(tmp_path)

    active_df, excluded_df = filter_dataset(raw_df)
    active_df = clean_and_normalize(active_df)

    # حفظ المستبعدات إن وجدت للمراجعة
    if not excluded_df.empty:
        excl_file = CLEAN_DIR / "excluded_products.csv"
        excluded_df.to_csv(excl_file, index=False, encoding="utf-8-sig")
        log.info(f"تم حفظ {len(excluded_df):,} منتج مستبعد في: {excl_file.name}")

    # حفظ المنتجات النشطة
    out_pkl = CLEAN_DIR / "salla_active_products.pkl"
    out_csv = CLEAN_DIR / "salla_active_products.csv"
    active_df.to_pickle(out_pkl)
    active_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    log.info(f"تم حفظ المنتجات النشطة المعتمدة في: {out_pkl.name} و {out_csv.name}")
    log.info(f"العدد النهائي الجاهز للتقسيم: {len(active_df):,} منتج")
