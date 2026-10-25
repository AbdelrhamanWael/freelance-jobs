# -*- coding: utf-8 -*-
"""
استخراج بيانات معلمي القدرات من تويتر/X
يقوم هذا السكربت بـ:
1. جلب البيانات تلقائياً عبر Apify API (يدعم xquik~x-tweet-scraper و apidojo~tweet-scraper)
2. قراءة dataset.json محلياً إن وُجد (Offline Mode)
3. معالجة وتوحيد أرقام الهواتف السعودية بصيغة 9665XXXXXXXX
4. دعم الأرقام المشرقية (٠-٩)، روابط واتساب المختصرة wa.me، والفواصل والمسافات
5. استخراج التخصص (كمي، لفظي، شامل)
6. منع التكرار على مستوى اسم المستخدم ورقم الجوال لضمان 30 معلماً فريداً
7. حفظ ملف qudrat_teachers.csv جاهز للاستخدام في Excel باللغة العربية
"""

import os
import sys
import json
import re
import csv
import time
from typing import Optional, Dict, List

# ضبط إخراج الطرفية ليدعم UTF-8 على أنظمة ويندوز
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
DATASET_FILE = "dataset.json"
OUTPUT_CSV = "qudrat_teachers.csv"
TARGET_COUNT = 30

# نستخدم xquik~x-tweet-scraper لأنه يسمح بسحب مئات التغريدات في الخطة المجانية
# (بينما apidojo يضع حداً أقصى 10 تغريدات لحسابات Free)
ACTOR_ID = "xquik~x-tweet-scraper"

SEARCH_TERMS = [
    '("قدرات" OR "قدرات الورقي" OR "قدرات كمي" OR "قدرات لفظي") ("واتس" OR "واتساب" OR "wa.me" OR "للتواصل") lang:ar -filter:replies',
    '("مدرس قدرات" OR "معلم قدرات" OR "أستاذ قدرات" OR "خصوصي قدرات") ("واتس" OR "واتساب" OR "wa.me") lang:ar',
    '("دورة قدرات" OR "شرح قدرات") ("05" OR "٩٦٦٥" OR "wa.me") lang:ar'
]

ACTOR_INPUT = {
    "searchTerms": SEARCH_TERMS,
    "maxItems": 400,
    "queryType": "Latest"
}

# جدول تحويل الأرقام العربية/المشرقية (٠-٩) إلى أرقام قياسية (0-9)
ARABIC_DIGITS_MAP = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_text(text: str) -> str:
    """تحويل الأرقام المشرقية إلى قياسية"""
    if not text:
        return ""
    return str(text).translate(ARABIC_DIGITS_MAP)


def extract_saudi_phone(text: str) -> Optional[str]:
    """
    استخراج وتوحيد رقم الجوال السعودي بالصيغة الدولية: 9665XXXXXXXX
    يدعم:
    - روابط الواتساب: wa.me, api.whatsapp.com
    - الأرقام المكتوبة بفواصل أو مسافات أو شرطات أو بدونها
    - الأرقام المشرقية (٠٥...)
    """
    if not text:
        return None

    clean_text = normalize_text(text)

    # 1. فحص روابط واتساب المباشرة
    wa_match = re.search(r'(?:wa\.me|api\.whatsapp\.com/send\?phone=)/?\+?(\d+)', clean_text)
    if wa_match:
        digits = wa_match.group(1)
        if digits.startswith("00966"):
            digits = digits[5:]
        elif digits.startswith("966"):
            digits = digits[3:]
        elif digits.startswith("0"):
            digits = digits[1:]
        
        if len(digits) == 9 and digits.startswith("5"):
            return f"966{digits}"

    # 2. فحص أرقام الهواتف السعودية في النص مع التأكد من حدود الرقم لمنع التداخل مع المفاتيح الدولية
    pattern = r'(?<!\d)(?:(?:\+?966|00966|0)\s*)?5[\s\-_.]*[0123456789](?:[\s\-_.]*\d){7}(?!\d)'
    for match in re.finditer(pattern, clean_text):
        raw = match.group()
        digits = re.sub(r'\D', '', raw)
        if digits.startswith("00966"):
            digits = digits[5:]
        elif digits.startswith("966"):
            digits = digits[3:]
        elif digits.startswith("0"):
            digits = digits[1:]
            
        if len(digits) == 9 and digits.startswith("5"):
            return f"966{digits}"

    return None


def get_specialty(text: str) -> str:
    """تحديد التخصص بناءً على الكلمات المفتاحية"""
    t = text.lower()
    kinds = []
    if re.search(r'كمي|رياضيات|حساب', t):
        kinds.append("كمي")
    if re.search(r'لفظي|لغة عربية|استيعاب|تناظر', t):
        kinds.append("لفظي")
    return " + ".join(kinds) if kinds else "قدرات (عام)"


def fetch_from_apify(token: str) -> List[Dict]:
    """تشغيل الـ Actor وجلب البيانات مباشرة عبر Apify REST API"""
    try:
        import requests
    except ImportError:
        print("[!] مكتبة requests غير مثبتة. قم بتثبيتها عبر: pip install requests")
        return []

    headers = {"Authorization": f"Bearer {token}"}
    print("[*] جارٍ التحقق من الحساب على Apify...")
    
    user_res = requests.get("https://api.apify.com/v2/users/me", headers=headers)
    if user_res.status_code != 200:
        print(f"[!] خطأ في التوكن (Status {user_res.status_code}): {user_res.text}")
        return []

    user_data = user_res.json().get("data", {})
    username = user_data.get("username")
    print(f"[✓] تم الاتصال بنجاح بالحساب: {username}")

    limits = user_data.get("effectivePlatformFeatures", {}).get("ACTORS", {})
    if limits.get("isEnabled") is False:
        print(f"\n[!] تنبيه: لا يمكن تشغيل الـ Actor على هذا الحساب بسبب تجاوز الحد المجاني:")
        print(f"    السبب: {limits.get('disabledReason')}")
        return []

    print(f"[*] جارٍ إرسال مهمة السحب إلى الـ Actor ({ACTOR_ID})...")
    run_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"
    run_res = requests.post(run_url, headers=headers, json=ACTOR_INPUT)
    if run_res.status_code not in (200, 201):
        print(f"[!] فشل بدء المهمة: {run_res.text}")
        return []

    run_info = run_res.json().get("data", {})
    run_id = run_info.get("id")
    dataset_id = run_info.get("defaultDatasetId")
    print(f"[✓] بدأت المهمة بنجاح (Run ID: {run_id})")
    print("[*] جارٍ انتظار اكتمال سحب التغريدات...")

    # متابعة حالة التشغيل
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    while True:
        time.sleep(5)
        check_res = requests.get(status_url, headers=headers).json().get("data", {})
        status = check_res.get("status")
        print(f"    - الحالة الحالية: {status}")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status != "SUCCEEDED":
        print(f"[!] انتهت المهمة بحالة غير ناجحة: {status}")
        return []

    print(f"[*] جارٍ تحميل التغريدات من الـ Dataset ({dataset_id})...")
    items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true&format=json"
    items_res = requests.get(items_url, headers=headers)
    if items_res.status_code == 200:
        items = items_res.json()
        print(f"[✓] تم جلب {len(items)} تغريدة من Apify.")
        # حفظ نسخة احتياطية محلية
        with open(DATASET_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        return items
    else:
        print(f"[!] فشل تحميل عناصر الـ Dataset: {items_res.text}")
        return []


def process_dataset(items: List[Dict], target_count: int = TARGET_COUNT) -> List[List[str]]:
    """معالجة وتصفية بيانات المدرسين واستخراج الهواتف"""
    seen_users = set()
    seen_phones = set()
    rows = []

    for it in items:
        # استخراج بيانات المؤلف (يدعم كلا من apidojo و xquik)
        author = it.get("author") or {}
        user = author.get("userName") or author.get("username") or it.get("screen_name") or ""
        name = author.get("name") or it.get("name") or user

        # تجميع النصوص المحتمل احتواؤها على الرقم
        tweet_text = it.get("text") or it.get("full_text") or ""
        author_bio = (
            author.get("description")
            or author.get("bio")
            or author.get("profile_bio", {}).get("description")
            or ""
        )
        
        # استخراج الروابط الموسعة إن وجدت لتفادي اختصارات t.co
        expanded_urls = []
        entities = it.get("entities") or {}
        for u in entities.get("urls", []):
            exp = u.get("expanded_url")
            if exp:
                expanded_urls.append(exp)
        for u in it.get("urls", []):
            if isinstance(u, dict) and u.get("expanded_url"):
                expanded_urls.append(u.get("expanded_url"))
            elif isinstance(u, str):
                expanded_urls.append(u)

        blob = f"{tweet_text} {author_bio} {' '.join(expanded_urls)}"
        phone = extract_saudi_phone(blob)

        # استبعاد من ليس لديه رقم سعودي
        if not phone:
            continue

        # منع التكرار على مستوى اسم المستخدم أو رقم الجوال
        user_lower = user.lower()
        if (user_lower and user_lower in seen_users) or phone in seen_phones:
            continue

        if user_lower:
            seen_users.add(user_lower)
        seen_phones.add(phone)

        user_url = f"https://x.com/{user}" if user else "غير متوفر"
        spec = get_specialty(blob)

        rows.append([name, user_url, spec, phone])

        if len(rows) >= target_count:
            break

    return rows


def main():
    items = []

    # 1. التحقق أولاً من وجود ملف dataset.json محلي
    if os.path.exists(DATASET_FILE):
        print(f"[*] تم العثور على ملف محلي ({DATASET_FILE}). جارٍ قراءته...")
        try:
            with open(DATASET_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
            print(f"[✓] تم تحميل {len(items)} عنصر من الملف المحلي.")
        except Exception as e:
            print(f"[!] خطأ أثناء قراءة الملف المحلي: {e}")

    # 2. إذا لم يكن هناك ملف محلي، نجلب مباشرة عبر Apify
    if not items:
        if APIFY_TOKEN:
            print("[*] جارٍ السحب الآلي عبر Apify API...")
            items = fetch_from_apify(APIFY_TOKEN)
        else:
            print(f"[!] لم يتم العثور على ملف {DATASET_FILE} ولم يتم تحديد APIFY_TOKEN فعال.")
            return

    if not items:
        print("[!] لم تتوفر أي بيانات للمعالجة.")
        return

    # 3. تنظيف واستخراج البيانات
    print(f"[*] جارٍ تنظيف البيانات واستخراج المعلمين الفريدين (المستهدف: {TARGET_COUNT})...")
    rows = process_dataset(items, target_count=TARGET_COUNT)

    # 4. حفظ النتيجة في ملف CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["الاسم", "رابط الحساب", "التخصص", "رقم الواتساب"])
        writer.writerows(rows)

    print("\n" + "="*50)
    print(f"[✓] اكتملت العملية بنجاح!")
    print(f"[✓] تم استخراج {len(rows)} معلماً فريداً.")
    print(f"[✓] تم حفظ النتائج في الملف: {OUTPUT_CSV}")
    print("="*50)


if __name__ == "__main__":
    main()
