# -*- coding: utf-8 -*-
import sys
import re
import json
import requests
import scrapetube
from extract_teachers import extract_saudi_phone, get_specialty

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

search_queries = [
    "قدرات 050",
    "قدرات 053",
    "قدرات 055",
    "قدرات 054",
    "قدرات 056",
    "قدرات 058",
    "قدرات كمي واتساب",
    "قدرات لفظي واتساب",
    "مدرس قدرات واتس",
    "معلم قدرات واتس",
    "معلمة قدرات واتس",
    "شرح قدرات واتس",
    "قدرات wa.me/966",
    "خصوصي قدرات واتساب",
    "تجميعات قدرات للتواصل",
]

EXCLUDE_WORDS = [
    "منصة", "مركز", "أكاديمية", "اكاديمية", "معهد", "مؤسسة", 
    "اخبار", "أخبار", "اسال", "إسأل", "خدمات", "متعهده", "متعهد", 
    "نختبر", "جريدة", "تسجيل جامعات", "قروب", "قناة"
]

found = []
seen_channels = set()
seen_phones = set()

for q in search_queries:
    print(f"[*] Searching YouTube for: {q}")
    try:
        videos = scrapetube.get_search(q, limit=25)
        for v in videos:
            vid = v.get("videoId")
            channel = v.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
            title = v.get("title", {}).get("runs", [{}])[0].get("text", "")
            
            # Check exclusions
            if any(w in channel for w in EXCLUDE_WORDS) or any(w in title for w in EXCLUDE_WORDS):
                continue
                
            snippets = v.get("detailedMetadataSnippets", [{}])[0].get("snippetText", {}).get("runs", [])
            snippet_text = " ".join([s.get("text", "") for s in snippets])
            
            combined = f"{channel} {title} {snippet_text}"
            phone = extract_saudi_phone(combined)
            
            if not phone and vid:
                try:
                    res = requests.get(f"https://www.youtube.com/watch?v={vid}", headers=headers, timeout=4)
                    m = re.search(r'"shortDescription":"(.*?)"', res.text)
                    if m:
                        desc = m.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
                        combined += f" {desc}"
                        phone = extract_saudi_phone(combined)
                except Exception:
                    pass
                    
            if phone:
                ch_key = channel.strip().lower()
                if ch_key not in seen_channels and phone not in seen_phones:
                    seen_channels.add(ch_key)
                    seen_phones.add(phone)
                    spec = get_specialty(combined)
                    url = f"https://www.youtube.com/watch?v={vid}"
                    found.append({
                        "name": channel,
                        "platform": "YouTube",
                        "url": url,
                        "specialty": spec,
                        "phone": phone,
                        "title": title
                    })
                    print(f"  [✓] FOUND: {channel} | {spec} | {phone} | {url}")
    except Exception as e:
        print(f"  [!] Error with query {q}: {e}")

print(f"\n[✓] Total YouTube teachers found: {len(found)}")
with open("youtube_teachers.json", "w", encoding="utf-8") as f:
    json.dump(found, f, ensure_ascii=False, indent=2)
