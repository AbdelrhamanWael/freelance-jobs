# -*- coding: utf-8 -*-
import sys
import re
import json
import requests
import scrapetube
from concurrent.futures import ThreadPoolExecutor, as_completed
from extract_teachers import extract_saudi_phone, get_specialty

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

EXCLUDE_WORDS = [
    "منصة", "مركز", "أكاديمية", "اكاديمية", "معهد", "مؤسسة", "شركة", "مكتب",
    "اخبار", "أخبار", "اسال", "إسأل", "خدمات", "متعهده", "متعهد", "نختبر",
    "جريدة", "تسجيل", "قروب", "قناة", "دليل", "استديو", "استوديو", "platform",
    "أخبار", "اخبارية", "شذى", "متجر", "مطبخ", "عقارات", "تسويق"
]

def is_individual_teacher(name: str) -> bool:
    if not name:
        return False
    lower = name.lower()
    if any(w in lower for w in EXCLUDE_WORDS):
        return False
    return True

def fetch_video_details(video_item):
    vid = video_item.get("videoId")
    channel = video_item.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
    title = video_item.get("title", {}).get("runs", [{}])[0].get("text", "")
    
    if not is_individual_teacher(channel):
        return None
        
    snippets = video_item.get("detailedMetadataSnippets", [{}])[0].get("snippetText", {}).get("runs", [])
    snippet_text = " ".join([s.get("text", "") for s in snippets])
    
    combined = f"{channel} {title} {snippet_text}"
    phone = extract_saudi_phone(combined)
    
    if not phone and vid:
        try:
            r = requests.get(f"https://www.youtube.com/watch?v={vid}", headers=headers, timeout=3)
            idx = r.text.find('"shortDescription":"')
            if idx != -1:
                end_idx = r.text.find('","isCrawlable":', idx)
                if end_idx != -1:
                    raw_desc = r.text[idx + 20:end_idx]
                    desc = raw_desc.encode("utf-8").decode("unicode_escape", errors="ignore")
                    combined += f" {desc}"
                    phone = extract_saudi_phone(combined)
        except Exception:
            pass
            
    if phone:
        spec = get_specialty(combined)
        return {
            "name": channel.strip(),
            "platform": "YouTube",
            "url": f"https://www.youtube.com/watch?v={vid}",
            "specialty": spec,
            "phone": phone,
            "title": title
        }
    return None

def main():
    search_queries = [
        "شرح قدرات كمي 05",
        "شرح قدرات لفظي 05",
        "مدرس خصوصي قدرات 05",
        "معلم خصوصي قدرات 05",
        "معلمة خصوصي قدرات 05",
        "أستاذ قدرات واتساب",
        "الاستاذ قدرات واتس 05",
        "المدرب قدرات واتس 05",
        "المدربة قدرات واتس 05",
        "تجميعات القدرات واتس 05",
        "حل نماذج القدرات واتس 05",
        "دورة تأسيس قدرات واتس 05",
        "قدرات محوسب واتس 05",
        "قدرات ورقي واتس 05",
        "معلم قدرات بالرياض 05",
        "معلم قدرات بجدة 05",
        "معلم قدرات بالشرقية 05",
        "مهندس قدرات واتس 05"
    ]
    
    # Load existing teachers if any
    found_teachers = []
    seen_names = set()
    seen_phones = set()
    try:
        with open("youtube_teachers.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
            for t in existing:
                if is_individual_teacher(t["name"]):
                    name_key = t["name"].strip().lower()
                    seen_names.add(name_key)
                    seen_phones.add(t["phone"])
                    found_teachers.append(t)
    except Exception:
        pass
        
    print(f"[*] المعلمون الحاليون في القائمة: {len(found_teachers)}")
    print("[*] جارٍ البحث الموسع في يوتيوب...")
    
    collected_videos = []
    seen_vids = set()
    
    for q in search_queries:
        try:
            v_list = scrapetube.get_search(q, limit=20)
            for v in v_list:
                vid = v.get("videoId")
                if vid and vid not in seen_vids:
                    seen_vids.add(vid)
                    collected_videos.append(v)
        except Exception as e:
            pass
            
    print(f"[✓] تم جمع {len(collected_videos)} فيديو إضافي...")
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch_video_details, v) for v in collected_videos]
        for f in as_completed(futures):
            res = f.result()
            if res:
                name_key = res["name"].strip().lower()
                phone = res["phone"]
                if name_key not in seen_names and phone not in seen_phones:
                    seen_names.add(name_key)
                    seen_phones.add(phone)
                    found_teachers.append(res)
                    print(f"  [+] معلم جديد من يوتيوب: {res['name']} | {res['specialty']} | {res['phone']}")
                    
    print(f"\n[✓] إجمالي المعلمين المستخرجين من يوتيوب بعد التوسيع: {len(found_teachers)}")
    with open("youtube_teachers.json", "w", encoding="utf-8") as f:
        json.dump(found_teachers, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
