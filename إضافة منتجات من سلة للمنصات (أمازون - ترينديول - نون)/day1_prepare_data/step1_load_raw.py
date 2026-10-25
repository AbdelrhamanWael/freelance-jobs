"""
step1_load_raw.py
=================
الخطوة الأولى: تحميل ملف التصدير الخام من سلة، الكشف التلقائي عن صف الترويسة،
وإعادة تسمية الأعمدة لتطابق الهيكل البرمجي الموحد.
"""

import sys
from pathlib import Path

# ضمان ترميز UTF-8 في شاشات ويندوز
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import logging
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from day1_prepare_data.config import (
    SALLA_EXPORT_PATH, ALT_EXPORT_PATH, COL_MAP, LOGS_DIR, CLEAN_DIR
)

# ── إعداد التسجيل ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "day1.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def resolve_file_path() -> Path:
    """تحديد مسار الملف إما من data/raw/ أو من المجلد الرئيسي."""
    if SALLA_EXPORT_PATH.exists():
        return SALLA_EXPORT_PATH
    if ALT_EXPORT_PATH.exists():
        log.info(f"تم العثور على الملف في المسار البديل: {ALT_EXPORT_PATH.name}")
        return ALT_EXPORT_PATH
    log.error("لم يتم العثور على ملف تصدير سلة في data/raw/ أو في المجلد الرئيسي.")
    sys.exit(1)


def load_salla_export(path: Path) -> pd.DataFrame:
    """
    قراءة الملف وتحديد صف الترويسة الفعلي تلقائياً.
    ملفات سلة عادة ما تحتوي على شريط 'بيانات المنتج' في الصف الأول والترويسة في الصف الثاني.
    """
    suffix = path.suffix.lower()
    log.info(f"جاري قراءة الملف: {path.name} ({path.stat().st_size / 1024:.1f} KB)")

    if suffix in (".xlsx", ".xls"):
        # فحص أول صفين لتحديد موقع الترويسة
        preview = pd.read_excel(path, header=None, nrows=3)
        row0_str = " ".join([str(x) for x in preview.iloc[0].values])
        if "بيانات المنتج" in row0_str or preview.iloc[0].isna().sum() > len(preview.columns) // 2:
            log.info("تم رصد ترويسة سلة المزدوجة — جاري التحميل بدءاً من الصف الثاني (header=1)...")
            df = pd.read_excel(path, header=1, dtype=str)
        else:
            df = pd.read_excel(path, header=0, dtype=str)

    elif suffix == ".csv":
        try:
            df = pd.read_csv(path, header=0, dtype=str, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df = pd.read_csv(path, header=0, dtype=str, encoding="cp1256")
    else:
        log.error(f"صيغة الملف غير مدعومة: {suffix}")
        sys.exit(1)

    # إزالة الفراغات الزائدة من أسماء الأعمدة
    df.columns = [str(c).strip() for c in df.columns]
    log.info(f"تم تحميل الملف بنجاح: {len(df):,} صف | {len(df.columns)} عمود")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """إعادة تسمية الأعمدة وفق خريطة COL_MAP."""
    # إعداد خريطة مطابقة بدون فراغات
    cleaned_col_map = {k.strip(): v for k, v in COL_MAP.items()}
    existing_map = {c: cleaned_col_map[c] for c in df.columns if c in cleaned_col_map}
    
    df = df.rename(columns=existing_map)
    log.info(f"تمت مطابقة وإعادة تسمية {len(existing_map)} عمود أساسي بنجاح.")
    return df


if __name__ == "__main__":
    file_path = resolve_file_path()
    raw_df = load_salla_export(file_path)
    renamed_df = rename_columns(raw_df)

    out_file = CLEAN_DIR / "_raw_renamed.pkl"
    renamed_df.to_pickle(out_file)
    log.info(f"تم حفظ البيانات الأولية في: {out_file.name}")
