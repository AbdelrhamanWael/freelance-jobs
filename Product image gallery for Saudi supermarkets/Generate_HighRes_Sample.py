import os
import csv
import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_bing_image(query):
    try:
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&form=HDRSC2"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # Find the first murl (media url)
        match = re.search(r'murl&quot;:&quot;(.*?)&quot;', html)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    return None

def download_high_res_sample():
    import urllib.parse
    folder_name = "Supermarket_HighRes_Sample"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print("جاري تجهيز العينة عالية الدقة باستخدام Bing Images...")

    products = [
        {"name": "حليب المراعي طازج كامل الدسم 1 لتر", "category": "ألبان وأجبان", "query": "Almarai fresh milk full fat 1L"},
        {"name": "لبن نادك طازج 2.9 لتر", "category": "ألبان وأجبان", "query": "Nadec fresh laban"},
        {"name": "زبادي الصافي طازج كامل الدسم", "category": "ألبان وأجبان", "query": "Alsafi yoghurt full fat"},
        {"name": "بيض المائدة الوطنية حجم كبير", "category": "ألبان وأجبان", "query": "Al watania eggs"},
        {"name": "شيبس ليز كاتشب", "category": "تسالي وشيبس", "query": "Lays ketchup chips"},
        {"name": "شيبس دوريتوس جبنة الناتشو", "category": "تسالي وشيبس", "query": "Doritos nacho cheese"},
        {"name": "شوكولاتة جالاكسي بالحليب ناعمة", "category": "حلويات", "query": "Galaxy milk chocolate bar"},
        {"name": "شوكولاتة سنيكرز بالكراميل والفول السوداني", "category": "حلويات", "query": "Snickers chocolate bar"},
        {"name": "عصير ربيع برتقال 200 مل", "category": "مشروبات", "query": "Al rabie orange juice"},
        {"name": "مياه نوفا 330 مل", "category": "مشروبات", "query": "Nova water bottle"},
        {"name": "بيبسي علب 330 مل", "category": "مشروبات", "query": "Pepsi can 330ml"},
        {"name": "جبنة بوك كاسات 500 جرام", "category": "ألبان وأجبان", "query": "Puck cream cheese jar"}
    ]

    csv_file = os.path.join(folder_name, "Products_Database_Sample.csv")
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["Barcode", "Product Name", "Category", "Image File Name", "Image URL"])
        
        for i, prod in enumerate(products):
            print(f"جاري البحث عن صورة لـ: {prod['name']}")
            barcode = "628" + str(100000000 + i * 12345)
            
            img_url = get_bing_image(prod["query"])
            if img_url:
                try:
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    img_data = urllib.request.urlopen(req, timeout=10).read()
                    
                    file_name = f"{barcode}.jpg"
                    file_path = os.path.join(folder_name, file_name)
                    
                    with open(file_path, "wb") as img_f:
                        img_f.write(img_data)
                    
                    writer.writerow([barcode, prod["name"], prod["category"], file_name, img_url])
                    print(f"تم تحميل صورة {prod['name']} بنجاح!")
                except Exception as e:
                    print(f"فشل تحميل صورة {prod['name']}: {e}")
            else:
                print(f"لم يتم العثور على صورة لـ {prod['name']}")

    print(f"\n✅ تمت العملية بنجاح! العينة الجديدة محفوظة في مجلد {folder_name}")

if __name__ == "__main__":
    download_high_res_sample()
