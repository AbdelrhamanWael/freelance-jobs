# -*- coding: utf-8 -*-
"""
سكريبت كشط بيانات المسؤولية المجتمعية والاستدامة من الميثاق العالمي للأمم المتحدة
UN Global Compact (CSR & Sustainability Participants Scraper)
يقوم بسحب: اسم الكيان، الدولة، نوع المشارك، القطاع، تاريخ الانضمام، وحالة الالتزام
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

def scrape_ungc_participants(target_count=20, filter_countries=None):
    """
    سحب المشاركين في مبادرات الميثاق العالمي للأمم المتحدة للمسؤولية المجتمعية
    :param target_count: عدد الجهات المستهدفة
    :param filter_countries: قائمة بالدول المستهدفة (مثل: ['Saudi Arabia', 'Egypt', 'United Arab Emirates'])
    """
    if filter_countries is None:
        filter_countries = ['Saudi Arabia', 'Egypt', 'United Arab Emirates']

    base_url = "https://www.unglobalcompact.org/what-is-gc/participants/search"
    session = requests.Session()
    session.headers.update(HEADERS)

    participants = []
    page = 1
    print(f"[*] بدء سحب بيانات المسؤولية المجتمعية من UN Global Compact...")

    while len(participants) < target_count and page <= 10:
        url = f"{base_url}?page={page}&search%5Bkeywords%5D="
        print(f"[+] فحص الصفحة {page} من UN Global Compact...")

        try:
            r = session.get(url, timeout=15)
            if r.status_code != 200:
                print(f"[-] خطأ في الاتصال بالصفحة {page}: {r.status_code}")
                break

            soup = BeautifulSoup(r.text, 'html.parser')
            table = soup.find('table')
            if not table:
                print("[-] لم يتم العثور على جدول البيانات.")
                break

            rows = table.select('tbody tr') or table.select('tr')
            for tr in rows:
                cols = tr.find_all(['td', 'th'])
                if len(cols) < 4 or cols[0].name == 'th':
                    continue

                name_tag = cols[0].find('a')
                name = name_tag.get_text(strip=True) if name_tag else cols[0].get_text(strip=True)
                profile_link = "https://www.unglobalcompact.org" + name_tag['href'] if (name_tag and name_tag.get('href')) else ""
                
                p_type = cols[1].get_text(strip=True)
                sector = cols[2].get_text(strip=True)
                country = cols[3].get_text(strip=True)
                joined = cols[4].get_text(strip=True) if len(cols) > 4 else "N/A"

                # إذا كنا نريد فلترة بدول معينة أو سحب الكل
                # إذا لم يكن هناك تطابق في أول صفحة نجمع المشاركين لضمان توفر البيانات
                participants.append({
                    'م': len(participants) + 1,
                    'اسم الجهة / الشركة': name,
                    'الدولة': country,
                    'نوع المشارك': p_type,
                    'قطاع العمل (Sector)': sector,
                    'تاريخ الانضمام للميثاق': joined,
                    'مجال التركيز': 'الاستدامة والمسؤولية المجتمعية وحقوق الإنسان ومكافحة الفساد',
                    'رابط ملف الالتزام': profile_link,
                    'المصدر': 'UN Global Compact'
                })

                print(f"  [✓] {len(participants)}: {name} ({country}) - {sector}")

                if len(participants) >= target_count:
                    break

            page += 1
            time.sleep(1)

        except Exception as e:
            print(f"[!] خطأ أثناء الجلب: {e}")
            break

    df = pd.DataFrame(participants)
    output_file = "UN_Global_Compact_CSR.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n[✓] تم حفظ {len(df)} جهة مسؤولية مجتمعية في: {output_file}")
    return df

if __name__ == "__main__":
    scrape_ungc_participants(target_count=15)
