# -*- coding: utf-8 -*-
"""
سكريبت كشط بيانات الشركات والجمعيات الأهلية في منطقة نجران
Najran Region Scraper (Yellow Pages SA Najran & Directories)
يستهدف جمع بيانات الشركات والمقاولات والجمعيات المسجلة في نطاق منطقة نجران ومحافظاتها
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
    'X-Requested-With': 'XMLHttpRequest'
}

def scrape_yellowpages_najran(max_pages=3, target_count=50):
    """
    سحب شركات ومقاولات منطقة نجران من دليل Yellow Pages السعودية
    الرابط: https://www.yellowpages.com.sa/ar/najran
    """
    base_url = "https://www.yellowpages.com.sa"
    search_url = f"{base_url}/ar/najran/page-"
    session = requests.Session()
    session.headers.update(HEADERS)

    najran_companies = []
    print(f"[*] بدء كشط الشركات والمقاولات في نطاق منطقة نجران...")

    for page in range(1, max_pages + 1):
        if len(najran_companies) >= target_count:
            break

        url = f"{search_url}{page}"
        print(f"[+] فحص الصفحة {page}: {url}")

        try:
            r = session.get(url, timeout=15)
            if r.status_code != 200:
                print(f"[-] كود الاستجابة {r.status_code}")
                continue

            soup = BeautifulSoup(r.text, 'html.parser')
            # عناصر الشركات في الصفحات الصفراء السعودية
            cards = soup.select('.item-row, .company-result, [data-company-id], .companyCards > div')
            call_buttons = soup.select('[data-tooltip-phones]')

            print(f"[i] تم العثور على {len(call_buttons)} جهة في هذه الصفحة.")

            for btn in call_buttons:
                if len(najran_companies) >= target_count:
                    break

                parent = btn
                for _ in range(4):
                    if parent and parent.parent:
                        parent = parent.parent

                name_tag = parent.find(['h2', 'h3', 'a'], class_=lambda c: c and any(k in str(c).lower() for k in ['title', 'name', 'heading']))
                name = name_tag.get_text(strip=True) if name_tag else "غير متوفر"

                if not name or len(name) < 3 or any(c['اسم الجهة'] == name for c in najran_companies):
                    continue

                cat_tag = parent.find(class_=lambda c: c and any(k in str(c).lower() for k in ['category', 'categories', 'keywords']))
                category = cat_tag.get_text(strip=True) if cat_tag else "مقاولات وتجارة عامة"

                addr_tag = parent.find(class_=lambda c: c and any(k in str(c).lower() for k in ['address', 'location']))
                address = addr_tag.get_text(strip=True) if addr_tag else "نجران، المملكة العربية السعودية"

                # استدعاء رقم الهاتف عبر AJAX
                phone_endpoint = btn.get('data-tooltip-phones')
                phone = "غير متوفر"
                if phone_endpoint:
                    p_url = f"{base_url}{phone_endpoint}" if phone_endpoint.startswith('/') else phone_endpoint
                    try:
                        p_res = session.get(p_url, timeout=8)
                        if p_res.status_code == 200:
                            data = p_res.json()
                            if isinstance(data, list):
                                extracted = []
                                for sub in data:
                                    if isinstance(sub, list):
                                        extracted.extend([str(x) for x in sub if x])
                                if extracted:
                                    phone = " / ".join(extracted)
                    except Exception:
                        pass

                najran_companies.append({
                    'م': len(najran_companies) + 1,
                    'اسم الجهة': name,
                    'المنطقة': 'منطقة نجران',
                    'طبيعة النشاط': category,
                    'رقم التواصل': phone,
                    'العنوان': address,
                    'المصدر': 'Yellow Pages SA (Najran)'
                })
                print(f"  [✓] {len(najran_companies)}: {name} | {phone} | {category[:30]}")

            time.sleep(1.5)

        except Exception as e:
            print(f"[!] استثناء أثناء الفحص: {e}")
            continue

    if najran_companies:
        df = pd.DataFrame(najran_companies)
        df.to_excel("YellowPages_Najran_Scraped.xlsx", index=False)
        print(f"[✓] تم حفظ {len(df)} جهة مسحوبة بنجاح.")
        return df
    return None

if __name__ == "__main__":
    scrape_yellowpages_najran(max_pages=2, target_count=10)
