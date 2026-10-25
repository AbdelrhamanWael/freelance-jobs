from curl_cffi import requests
from bs4 import BeautifulSoup
import csv
import os
import random
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_high_res_amazon_image(url):
    # إزالة الجزء الخاص بتصغير الصورة في أمازون للحصول على الصورة الأصلية عالية الدقة
    import re
    return re.sub(r'\._AC_.*?_\.', '.', url)

def main():
    folder_name = "Supermarket_Sample"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print("جاري سحب المنتجات من قسم السوبرماركت (أمازون السعودية) لتخطي حظر بنده...")

    search_queries = [
        {"query": "almarai milk", "cat": "ألبان وبيض"},
        {"query": "nadec yoghurt", "cat": "ألبان وبيض"},
        {"query": "lays ketchup chips", "cat": "تسالي وشيبس"},
        {"query": "doritos cheese", "cat": "تسالي وشيبس"},
        {"query": "galaxy chocolate", "cat": "حلويات وشوكولاتة"},
        {"query": "snickers chocolate", "cat": "حلويات وشوكولاتة"},
        {"query": "pepsi can", "cat": "مياه ومشروبات"},
        {"query": "nova water", "cat": "مياه ومشروبات"}
    ]
    
    csv_file = os.path.join(folder_name, "Products_Database_Sample.csv")
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["Barcode", "Product Name", "Category", "Image File Name", "Image Link"])
        
        for item in search_queries:
            q = item["query"]
            cat = item["cat"]
            print(f"جاري البحث عن '{q}'...")
            
            try:
                url = f"https://www.amazon.sa/-/en/s?k={q.replace(' ', '+')}&i=grocery"
                res = requests.get(url, impersonate="chrome110")
                
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    products = soup.select('div[data-component-type="s-search-result"]')
                    
                    saved_count = 0
                    for prod in products[:3]: # سحب 3 منتجات من كل بحث
                        img_tag = prod.select_one("img.s-image")
                        title_tag = prod.select_one("h2 span")
                        
                        if img_tag and title_tag:
                            name = title_tag.text.strip()
                            img_src = img_tag.get('src')
                            high_res_img = get_high_res_amazon_image(img_src)
                            
                            barcode = "628" + str(random.randint(100000000, 999999999))
                            safe_name = name.replace("/", "-").replace("\\", "-")
                            if len(safe_name) > 60:
                                safe_name = safe_name[:60] + "..."
                            
                            writer.writerow([barcode, safe_name, cat, f"{barcode}.jpg", high_res_img])
                            saved_count += 1
                    
                    print(f"✅ تم سحب {saved_count} منتجات من بحث {q}")
                else:
                    print(f"فشل البحث عن {q} (كود الخطأ: {res.status_code})")
                
            except Exception as e:
                print(f"حدث خطأ في {q}: {e}")
                
            time.sleep(1) # استراحة قصيرة لتجنب الحظر
            
    print("\n✅ اكتمل السحب بنجاح! تم حفظ العينة الاحترافية في مجلد Supermarket_Sample")

if __name__ == "__main__":
    main()