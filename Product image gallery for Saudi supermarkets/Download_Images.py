import csv
import os
import requests

def download_images():
    folder_name = "Supermarket_Sample"
    csv_file = os.path.join(folder_name, "Products_Database_Sample.csv")
    
    if not os.path.exists(csv_file):
        print("لم يتم العثور على ملف الإكسل!")
        return

    print("جاري تحميل صور المنتجات عالية الدقة...")
    
    with open(csv_file, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            img_url = row.get("Image Link")
            img_name = row.get("Image File Name")
            
            if img_url and img_name:
                try:
                    res = requests.get(img_url, timeout=10)
                    if res.status_code == 200:
                        img_path = os.path.join(folder_name, img_name)
                        with open(img_path, 'wb') as img_file:
                            img_file.write(res.content)
                        count += 1
                        print(f"تم تحميل: {img_name}")
                except Exception as e:
                    print(f"خطأ في تحميل {img_name}: {e}")
                    
    print(f"\n✅ تمت العملية! تم تحميل {count} صورة بنجاح داخل مجلد {folder_name}.")

if __name__ == "__main__":
    download_images()
