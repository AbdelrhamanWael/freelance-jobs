import os
import sys
from dotenv import load_dotenv
from apify_client import ApifyClient
from scraper import process_apify_items
from excel_exporter import (
    clean_phone_number,
    generate_whatsapp_url,
    validate_email,
    extract_city_and_district,
    deduplicate_records,
    enrich_emails_from_websites,
    build_excel_database
)

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()
token = os.getenv("APIFY_API_TOKEN")

print("=" * 65)
print("🚀 استكمال قاعدة البيانات إلى 1,000+ مطعم مع منع التكرار تماماً")
print("=" * 65)

# Step 1: Load existing clean records from previous runs
print("\n📥 [1/4] جلب وتدقيق السجلات السابقة من الدفعات المعتمدة...")
prev_token = os.getenv("PREV_APIFY_API_TOKEN", os.getenv("APIFY_API_TOKEN", ""))
prev_client = ApifyClient(prev_token)

existing_raw = []
try:
    ds1 = list(prev_client.dataset("hPghofqODJRCiRzoI").iterate_items())
    existing_raw.extend(ds1)
    print(f"  ✓ تم استدعاء {len(ds1)} سجل من الدفعة السابقة (hPghofqODJRCiRzoI)")
except Exception as e:
    print(f"  ⚠️ تنبيه: {e}")

try:
    ds2 = list(prev_client.dataset("ehbZM2gEejke59htG").iterate_items())
    existing_raw.extend(ds2)
    print(f"  ✓ تم استدعاء {len(ds2)} سجل من دفعة العينة (ehbZM2gEejke59htG)")
except Exception as e:
    pass

existing_cleaned = process_apify_items(existing_raw)
print(f"  📊 السجلات الفريدة المعتمدة المتاحة حالياً: {len(existing_cleaned)} مطعم")

needed_to_1000 = max(0, 1000 - len(existing_cleaned))
print(f"  🎯 العدد المطلوب بدقة لتخطي الـ 1000: {needed_to_1000} مطعم إضافي")

# Step 2: Target new specific areas using the fresh Apify Token
print(f"\n📡 [2/4] تشغيل Apify بالحساب الجديد لاستخراج مطاعم من مناطق جديدة لم تُسحب من قبل...")
new_client = ApifyClient(token)

fresh_queries = [
    "مطاعم الدرعية التاريخية والبجيري",
    "مطاعم الخرج والعزيزية",
    "مطاعم حي الصحافة والعقيق الرياض",
    "مطاعم حي النرجس والعارض الرياض",
    "مطاعم حي قرطبة واليرموك الرياض",
    "مطاعم ضاحية لبن وطويق الرياض",
    "مطاعم حي الشفا وبدر والعزيزية الرياض",
    "مطاعم حي الرمال والمونسية الرياض"
]

actor_input = {
    "searchStringsArray": fresh_queries,
    "locationQuery": "Riyadh, Saudi Arabia",
    "maxCrawledPlacesPerSearch": 40,
    "language": "ar",
    "countryCode": "sa",
    "skipClosedPlaces": True,
    "maxReviews": 0
}

print(f"  🔍 الاستعلامات الجديدة المستهدفة:")
for q in fresh_queries:
    print(f"     - {q}")

run = new_client.actor("compass/crawler-google-places").call(run_input=actor_input)
status = run.status if hasattr(run, "status") else (run.get("status") if isinstance(run, dict) else "UNKNOWN")
print(f"  ✅ اكتمل سحب الدفعة الجديدة بحالة: {status}")

dataset_id = run.default_dataset_id if hasattr(run, "default_dataset_id") else run["defaultDatasetId"]
print(f"  📥 جلب السجلات الجديدة من Dataset: {dataset_id}...")

new_items = list(new_client.dataset(dataset_id).iterate_items())
print(f"  ✓ تم جلب {len(new_items)} سجل جديد من Apify.")

# Step 3: Combine and strictly deduplicate (Same data is NEVER included twice)
print("\n🔄 [3/4] دمج السجلات وتطبيق الفلترة المزدوجة لمنع التكرار (Zero Duplication)...")
all_raw_combined = existing_raw + new_items
final_unique_records = process_apify_items(all_raw_combined)

print("\n" + "=" * 65)
print(f"🎯 إجمالي عدد المطاعم الفريدة بعد الدمج ومنع التكرار: {len(final_unique_records)} مطعم")
print("=" * 65)

if len(final_unique_records) >= 1000:
    print(f"✅ تحقق الشرط بنجاح تام! العدد يتجاوز 1,000 مطعم معتمد.")
else:
    print(f"⚠️ العدد الحالي: {len(final_unique_records)}")

# Step 4: Export to Excel
print("\n📊 [4/4] تصدير ملف الإكسل النهائي الشامل...")
output_file = "restaurants_database_riyadh_full.xlsx"
build_excel_database(final_unique_records, output_file)

print(f"\n🎉 تم الانتهاء بنجاح وحفظ الملف في: {output_file}")
