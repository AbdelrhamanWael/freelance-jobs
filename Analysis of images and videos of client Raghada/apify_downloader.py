import os
import sys
import logging
import requests
import pandas as pd
from apify_client import ApifyClient

# ----------------------------------------------------------------------------
# 1. إعدادات المتغيرات
# ----------------------------------------------------------------------------
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "YOUR_APIFY_API_TOKEN")
ACTOR_ID = "apify/facebook-posts-scraper"
EXCEL_FILE = "Excluded_Posts_31.xlsx"
OUTPUT_DIR = "Excluded_Posts_Media"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("download_media")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------------
# 2. قراءة الروابط من الإكسيل
# ----------------------------------------------------------------------------
logger.info(f"قراءة الروابط من {EXCEL_FILE}...")
df = pd.read_excel(EXCEL_FILE)

if "Post URL" not in df.columns:
    logger.error("لم يتم العثور على عمود Post URL في ملف الإكسيل!")
    sys.exit(1)

original_urls = df["Post URL"].dropna().tolist()
logger.info(f"تم العثور على {len(original_urls)} رابط.")

# بناء قاموس لربط الـ ID الخاص بالمنشور مع الـ Index ليتم تسميته Media_001, Media_002...
url_to_idx = {}
for i, url in enumerate(original_urls):
    url_to_idx[url] = i

# ----------------------------------------------------------------------------
# 3. تشغيل الـ Apify Actor
# ----------------------------------------------------------------------------
client = ApifyClient(APIFY_API_TOKEN)
start_urls = [{"url": u} for u in original_urls]

run_input = {
    "startUrls": start_urls,
    "resultsLimit": 100,
}

logger.info("جاري إرسال الروابط إلى Apify للبحث عن الميديا...")
try:
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if isinstance(run, dict):
        dataset_id = run.get("defaultDatasetId")
    else:
        dataset_id = getattr(run, "default_dataset_id", None)
        
    items = list(client.dataset(dataset_id).iterate_items())
    logger.info(f"تم استرجاع {len(items)} منشور من Apify.")
except Exception as e:
    logger.error(f"حدث خطأ أثناء الاتصال بـ Apify: {e}")
    sys.exit(1)

# ----------------------------------------------------------------------------
# 4. تحليل المخرجات وتحميل الميديا
# ----------------------------------------------------------------------------
def download_file(url, filepath):
    try:
        resp = requests.get(url, stream=True, timeout=15)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(1024 * 1024):
                    f.write(chunk)
            return True
    except Exception as e:
        logger.warning(f"فشل التحميل من {url}: {e}")
    return False

# لمحاولة مطابقة المنشور الراجع من Apify مع قائمتنا، سنعتمد على النص (Text) لأن الروابط (pfbid) تتغير في فيسبوك!
import json

def find_original_index_by_time(item_time, df):
    if not item_time:
        return -1
    for i, row in df.iterrows():
        orig_time = str(row.get("Publication Date & Time", "")).strip()
        if item_time == orig_time:
            return i
    return -1

# حفظ المخرجات الخام للمراجعة
with open("apify_raw_items.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

for item in items:
    item_url = item.get("url") or item.get("postUrl") or ""
    item_time = item.get("time") or ""
    
    idx = find_original_index_by_time(item_time, df)

    if idx == -1:
        logger.warning(f"لم أتمكن من مطابقة هذا المنشور مع الإكسيل باستخدام الوقت: {item_url} ({item_time})")
        continue
        
    prefix = f"Media_{idx + 1:03d}"
    attachments = item.get("attachments") or item.get("media") or []
    
    media_url = None
    media_ext = None
    
    # محاولة استخراج فيديو عالي الجودة أولاً
    for att in attachments:
        att_type = str(att.get("__typename", "")).lower() or str(att.get("type", "")).lower()
        if "video" in att_type:
            media_url = att.get("playable_url_quality_hd") or att.get("playable_url") or att.get("video")
            if media_url:
                media_ext = "mp4"
                break
            
    # إن لم نجد فيديو، نبحث عن صورة
    if not media_url:
        for att in attachments:
            att_type = str(att.get("__typename", "")).lower() or str(att.get("type", "")).lower()
            if "photo" in att_type or "image" in att_type:
                photo_obj = att.get("photo_image", {})
                media_url = photo_obj.get("uri") if isinstance(photo_obj, dict) else None
                if not media_url:
                    media_url = att.get("image") or att.get("thumbnail")
                if media_url:
                    media_ext = "jpg"
                    break
                
    # قد يكون الميديا مخزناً في الجذر (Top level) في بعض إصدارات Actor
    if not media_url:
        if item.get("videoUrl"):
            media_url = item.get("videoUrl")
            media_ext = "mp4"
        elif item.get("imageUrl"):
            media_url = item.get("imageUrl")
            media_ext = "jpg"
            
    if media_url:
        filepath = os.path.join(OUTPUT_DIR, f"{prefix}.{media_ext}")
        if os.path.exists(filepath):
            logger.info(f"الملف {filepath} موجود مسبقاً، سيتم التخطي.")
        else:
            logger.info(f"جاري تحميل: {filepath} ...")
            success = download_file(media_url, filepath)
            if success:
                logger.info(f"تم تحميل {filepath} بنجاح!")
            else:
                logger.error(f"فشل في تحميل {filepath}")
    else:
        logger.warning(f"لم يتم العثور على أي فيديو أو صورة في المنشور: {item_url}")

logger.info("انتهت عملية التحميل من Apify!")
