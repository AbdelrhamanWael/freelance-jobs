# -*- coding: utf-8 -*-
"""
سكريبت كشط بيانات الجمعيات الأهلية والجهات المانحة (Arab.org & NGO Directories)
Donors and Charities Directory Scraper
يقوم بسحب: اسم المؤسسة، الدولة، مجال العمل التنموي (تعليم، صحة، إغاثة)، والروابط الرسمية
"""

import sys
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
}

def scrape_arab_org_directory(country="saudi-arabia", target_count=15):
    """
    سحب المنظمات غير الربحية والمانحة من دليل Arab.org
    :param country: اسم الدولة في الرابط (saudi-arabia, egypt, uae, etc.)
    :param target_count: العدد المطلوب جمعه
    """
    base_url = f"https://arab.org/directory/category/{country}/"
    session = requests.Session()
    session.headers.update(HEADERS)
    
    donors = []
    print(f"[*] محاولة سحب الجهات المانحة من دليل Arab.org للدولة: {country}...")
    
    try:
        r = session.get(base_url, timeout=20)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # عناصر القوائم في Arab.org (قالب الووردبريس المخصص)
            cards = soup.select('.directorist-card, .listing-card, article.post, .entry-title')
            print(f"[i] تم العثور على {len(cards)} عنصر محتمل.")
            
            for c in cards:
                title_tag = c.find(['h2', 'h3', 'a'])
                if not title_tag:
                    continue
                name = title_tag.get_text(strip=True)
                link = title_tag.get('href') if title_tag.name == 'a' else (title_tag.find('a')['href'] if title_tag.find('a') else "")
                
                cat_tag = c.find(class_=lambda x: x and ('category' in x or 'cat' in x))
                category = cat_tag.get_text(strip=True) if cat_tag else "تنمية مجتمعية وإغاثة"

                if name and len(name) > 3 and not any(d['اسم المؤسسة'] == name for d in donors):
                    donors.append({
                        'م': len(donors) + 1,
                        'اسم المؤسسة': name,
                        'الدولة': country.capitalize(),
                        'مجال المنح والعمل': category,
                        'رابط التفاصيل': link,
                        'المصدر': 'Arab.org Directory'
                    })
                    print(f"  [✓] {len(donors)}: {name} | {category}")
                
                if len(donors) >= target_count:
                    break
        else:
            print(f"[-] الاستجابة من الموقع: {r.status_code}")
    except Exception as e:
        print(f"[!] تنبيه: موقع arab.org قد يفرض حماية Cloudflare أو حجب جغرافي مؤقت: {e}")
        print("[i] يمكنك استخدام المولد الرئيسي المرفق (build_full_database.py) الذي يتضمن بيانات موثقة بالكامل لـ 30 جهة مانحة معتمدة.")

    if donors:
        df = pd.DataFrame(donors)
        df.to_excel(f"Donors_{country}.xlsx", index=False)
        print(f"[✓] تم حفظ {len(df)} جهة في ملف Excel بنجاح.")
        return df
    return None

if __name__ == "__main__":
    scrape_arab_org_directory(country="saudi-arabia", target_count=10)
