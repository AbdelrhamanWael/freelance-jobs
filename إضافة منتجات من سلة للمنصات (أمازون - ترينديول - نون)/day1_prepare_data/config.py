# =============================================================================
#  config.py — إعدادات المشروع المركزية
# =============================================================================

from pathlib import Path

# ── مسارات الملفات ─────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
DATA_DIR  = BASE_DIR / "data"
RAW_DIR   = DATA_DIR / "raw"
CLEAN_DIR = DATA_DIR / "clean"
LOGS_DIR  = BASE_DIR / "logs"

for _dir in (RAW_DIR, CLEAN_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ── اسم ومسار ملف التصدير من سلة ──────────────────────────────────────────
SALLA_EXPORT_FILENAME = "salla_products_export.xlsx"
SALLA_EXPORT_PATH     = RAW_DIR / SALLA_EXPORT_FILENAME

# مسار بديل إذا كان الملف الأصلي في الجذر
ALT_EXPORT_PATH = BASE_DIR / "qitafaltabiea_13-09-2026-01-48_OZjH2K61peroLtoTcf55nd6F8O8zBkXe1ubO1qRS_products.xlsx"

# ── خريطة أعمدة سلة الفعلية -> أسماء برمجية موحدة ──────────────────────────
COL_MAP = {
    "No."                    : "product_id",
    "النوع "                 : "item_type",       # منتج | خيار
    "أسم المنتج"             : "name_ar",         # الاسم العربي
    "تصنيف المنتج"           : "category",        # الأقسام
    "صورة المنتج"            : "images",          # رابط الصورة الأساسية
    "وصف صورة المنتج"        : "image_alt",       # النص البديل
    "نوع المنتج"             : "product_type",    # منتج جاهز
    "سعر المنتج"             : "price",           # السعر الأساسي
    "الوصف"                  : "description",     # الوصف الكامل (HTML)
    "هل يتطلب شحن؟"          : "requires_shipping",
    "رمز المنتج sku"         : "sku",             # الباركود / SKU
    "سعر التكلفة"            : "cost_price",
    "السعر المخفض"           : "sale_price",
    "تاريخ بداية التخفيض"    : "sale_start",
    "تاريخ نهاية التخفيض"    : "sale_end",
    "الوزن"                  : "weight",
    "وحدة الوزن"             : "weight_unit",     # g | kg
    "حالة المنتج"            : "status",          # متاح | غير متاح | مخفي
    "الماركة"                : "brand",
    "العنوان الترويجي"        : "promo_title",
    "الباركود"               : "barcode",
    "MPN"                    : "mpn",
    "GTIN"                   : "gtin",
    "[1] الاسم"              : "option1_name",
    "[1] القيمة"             : "option1_value",
}

# ── الحالات المعتمدة كـ "نشط / متاح" ───────────────────────────────────────
# في منصة سلة: "متاح" تعني متوفر ونشط
ACTIVE_STATUS_VALUES = ["متاح", "active", "نشط", "available"]

# ── هل يتم فقط استبعاد المخفي (مخفي) أم حصر البيانات على المتاح فقط؟ ──────
# True  = فقط المنتجات بحالة "متاح"
# False = استبعاد "مخفي" فقط والإبقاء على الباقي (الخيار الثاني)
STRICT_ACTIVE_ONLY = False

# الكمية الافتراضية للمنتجات المتاحة (وغير المتاح يأخذ 0 تلقائياً)
DEFAULT_ACTIVE_STOCK = 10

# ── الأعمدة الأساسية المشتركة في الـ DataFrames النهائية ───────────────────
BASE_COLUMNS = [
    "product_id", "sku", "barcode", "name_ar",
    "price", "sale_price", "cost_price", "quantity",
    "status", "category", "brand",
    "weight_kg", "description", "images", "item_type"
]

