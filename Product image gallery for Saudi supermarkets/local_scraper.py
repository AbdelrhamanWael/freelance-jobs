import os
import sys
import io
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from playwright.sync_api import sync_playwright

def download_image(url, barcode, folder_name):
    if not url: return
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        img_response = requests.get(url, headers=headers, timeout=10)
        if img_response.status_code == 200:
            safe_barcode = str(barcode)[:50].strip().replace('/', '-').replace('\\', '-')
            file_name = f"{safe_barcode}.jpg"
            file_path = os.path.join(folder_name, file_name)
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
            print(f"تم تحميل: {file_name}")
    except Exception as e:
        print(f"خطأ في تحميل {barcode}: {e}")

def main():
    folder_name = "Supermarket_Sample_Local"
    os.makedirs(folder_name, exist_ok=True)
    
    print("جاري تشغيل المتصفح المحلي...")
    with sync_playwright() as p:
        # 1. تشغيل المتصفح بوضع مرئي (Headless=False) لكي تتمكن من رؤية ما يحدث وتخطي الحماية إذا لزم الأمر
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        print("الانتقال إلى موقع الدانوب...")
        page.goto("https://www.danube.sa/departments/dairy-eggs", timeout=60000)
        
        print("يرجى الانتظار، السكربت سيحاول إغلاق النافذة المنبثقة إذا ظهرت...")
        time.sleep(5)
        
        # 2. محاولة تخطي نافذة اختيار المدينة
        try:
            # البحث عن زر إغلاق النافذة (X)
            close_button = page.locator('.modal .close, button.close, [data-dismiss="modal"]').first
            if close_button.is_visible():
                print("تم العثور على زر الإغلاق X، جاري النقر...")
                close_button.click()
                time.sleep(5)
            else:
                # إذا لم يكن هناك زر X، سنجرب النقر على أي مكان خارج النافذة
                page.mouse.click(10, 10)
        except Exception as e:
            print("لم تظهر النافذة المنبثقة أو تعذر النقر عليها تلقائياً.")

        print("الآن سننتظر 10 ثوانٍ. إذا ظهر لك أي تحقق بشري (Cloudflare) أو نافذة مدينة، يرجى حلها يدوياً في المتصفح!")
        time.sleep(10)

        print("جاري النزول لأسفل الصفحة لتحميل المنتجات...")
        for _ in range(10):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(2)
            
        print("جاري استخراج بيانات المنتجات...")
        products = []
        
        # البحث عن جميع الصور في الصفحة
        images = page.locator("img").all()
        for img in images:
            src = img.get_attribute("src")
            alt = img.get_attribute("alt") or img.get_attribute("title")
            
            if src and src.startswith("http") and not "logo" in src.lower() and not "icon" in src.lower():
                # محاولة الحصول على اسم منطقي للمنتج
                name = alt if alt else f"product_{int(time.time() * 1000)}"
                products.append({
                    "barcode": name,
                    "image_url": src
                })
                
        print(f"تم العثور على {len(products)} صورة منتج!")
        
        for item in products:
            download_image(item['image_url'], item['barcode'], folder_name)
            
        print("تم الانتهاء!")
        browser.close()

if __name__ == "__main__":
    main()
