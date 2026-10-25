# -*- coding: utf-8 -*-
"""
سكريبت كشط بيانات الشركات من دليل الصفحات الصفراء (Yellow Pages)
Yellow Pages Production Scraper (Supports Egypt, Saudi Arabia, UAE)
يقوم بسحب: اسم الشركة، التصنيف/النشاط، العنوان، رابط الموقع، ورقم الهاتف (عبر استدعاء AJAX المباشر)
"""

import sys
import time
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ضبط ترميز الطرفية لدعم اللغة العربية في ويندوز
sys.stdout.reconfigure(encoding='utf-8')

# إعدادات المتصفح ورؤوس الطلبات لتفادي الحظر
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
    'X-Requested-With': 'XMLHttpRequest'
}

def fetch_phone_number(session, base_domain, phone_endpoint):
    """
    يقوم باستدعاء نقطة النهاية غير المتزامنة (AJAX) لسحب أرقام الهواتف
    حيث لا تظهر أرقام الهواتف مباشرة في كود الـ HTML الثابت
    """
    if not phone_endpoint:
        return "غير متوفر"
    
    phone_url = f"{base_domain}{phone_endpoint}" if phone_endpoint.startswith('/') else phone_endpoint
    try:
        res = session.get(phone_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            # النتيجة تأتي عادة في صيغة مصفوفة JSON: [["0100xxxxxxx"], [], []]
            data = res.json()
            if isinstance(data, list):
                phones = []
                for sublist in data:
                    if isinstance(sublist, list):
                        phones.extend([str(p) for p in sublist if p])
                if phones:
                    return " / ".join(phones)
    except Exception:
        pass
    return "غير متوفر"

def scrape_yellowpages(keyword="شركات", max_pages=3, target_count=50, country="eg"):
    """
    دالة الكشط الرئيسية لصفحات Yellow Pages
    :param keyword: كلمة البحث (مثلاً: شركات، مقاولات، أدوية، بترول)
    :param max_pages: الحد الأقصى للصفحات المطلوب فحصها
    :param target_count: العدد المطلوب جمعه (افتراضياً 50 شركة)
    :param country: كود الدولة (eg: مصر, sa: السعودية)
    """
    if country == "sa":
        base_domain = "https://www.yellowpages.com.sa"
        search_base = f"{base_domain}/ar/search/{keyword}/page-"
    else:
        base_domain = "https://yellowpages.com.eg"
        search_base = f"{base_domain}/ar/search/{keyword}/p"

    session = requests.Session()
    session.headers.update(HEADERS)
    
    collected_companies = []
    print(f"[*] بدء عملية الكشط من Yellow Pages ({country.upper()}) لكلمة البحث: '{keyword}'...")

    for page in range(1, max_pages + 1):
        if len(collected_companies) >= target_count:
            break
            
        page_url = f"{search_base}{page}"
        print(f"\n[+] جاري فحص الصفحة {page}: {page_url}")
        
        try:
            resp = session.get(page_url, timeout=15)
            if resp.status_code != 200:
                print(f"[-] فشل تحميل الصفحة {page} (كود الاستجابة: {resp.status_code})")
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # العثور على الحاوية الرئيسية للكروت أو العناصر ذات المعرف
            cards = soup.select('.item-row, .company-result, [data-company-id], .companyCards > div')
            
            # إذا لم يتم العثور على عناصر بالكلاسات أعلاه، نبحث عن أزرار الاتصال كعلامة استدلالية لكل شركة
            call_buttons = soup.select('[data-tooltip-phones]')
            
            print(f"[i] تم العثور على {len(call_buttons)} عنصر/جهة في هذه الصفحة.")
            
            for btn in call_buttons:
                if len(collected_companies) >= target_count:
                    break
                    
                # الصعود للحاوية الأم التي تضم بطاقة الشركة
                parent = btn
                for _ in range(4):
                    if parent and parent.parent:
                        parent = parent.parent
                        
                # 1. استخراج الاسم
                name_tag = parent.find(['h2', 'h3', 'a'], class_=lambda c: c and any(k in str(c).lower() for k in ['title', 'name', 'heading']))
                name = name_tag.get_text(strip=True) if name_tag else "غير متوفر"
                
                # تجاهل العناوين الفارغة أو الإعلانية العامة
                if not name or name in ["الصفحة الرئيسية", "غير متوفر"] or len(name) < 3:
                    continue
                    
                # منع تكرار نفس الشركة
                if any(c['اسم الجهة'] == name for c in collected_companies):
                    continue

                # 2. استخراج التصنيف / النشاط
                cat_tag = parent.find(class_=lambda c: c and any(k in str(c).lower() for k in ['category', 'categories', 'keywords']))
                category = cat_tag.get_text(strip=True) if cat_tag else "تجارة عامة وخدمات"

                # 3. استخراج العنوان
                addr_tag = parent.find(class_=lambda c: c and any(k in str(c).lower() for k in ['address', 'location']))
                address = addr_tag.get_text(strip=True) if addr_tag else "غير محدد"

                # 4. استخراج رقم الهاتف عبر AJAX
                phone_endpoint = btn.get('data-tooltip-phones')
                phone = fetch_phone_number(session, base_domain, phone_endpoint)

                # 5. استخراج رابط الموقع الإلكتروني
                web_tag = parent.find('a', href=lambda h: h and ('http' in h and 'yellowpages' not in h))
                website = web_tag.get('href') if web_tag else "غير متوفر"

                country_label = "المملكة العربية السعودية" if country == "sa" else "جمهورية مصر العربية"

                company_info = {
                    'م': len(collected_companies) + 1,
                    'اسم الجهة': name,
                    'الدولة': country_label,
                    'طبيعة النشاط': category,
                    'رقم التواصل': phone,
                    'الموقع الإلكتروني': website,
                    'العنوان': address,
                    'المصدر': f"Yellow Pages ({country.upper()})"
                }
                
                collected_companies.append(company_info)
                print(f"  [✓] {len(collected_companies)}: {name} | هاتف: {phone} | نشاط: {category[:30]}")

            # تأخير زمني بسيط لتجنب كشف البوتات (Politeness Delay)
            time.sleep(1.5)

        except Exception as e:
            print(f"[!] خطأ أثناء معالجة الصفحة {page}: {e}")
            continue

    # حفظ النتائج
    df = pd.DataFrame(collected_companies)
    output_file = f"YellowPages_Companies_{country.upper()}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\n[✓] تم بنجاح جمع {len(df)} شركة وتصديرها إلى الملف: {output_file}")
    return df

if __name__ == "__main__":
    # تشغيل تجريبي لسحب 10 شركات
    scrape_yellowpages(keyword="شركات", max_pages=2, target_count=10, country="eg")
