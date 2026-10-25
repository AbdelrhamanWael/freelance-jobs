import os
import sys
import io
import requests
from apify_client import ApifyClient
import time
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import csv

def generate_pro_sample():
    # مجلد الحفظ
    folder_name = "Pro_Sample_Saudi_Market"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print("جاري تشغيل السحب المتقدم لتجهيز العينة الاحترافية للعميل...")
    
    # تهيئة Apify
    token = os.environ.get("APIFY_API_TOKEN", "")
    client = ApifyClient(token)

    # سنقوم بالبحث عن 3 فئات مختلفة لضمان تنوع العينة
    target_urls = [
        {"url": "https://panda.sa/ar/categories/fresh-food/dairy-eggs", "category": "ألبان وبيض"},
        {"url": "https://panda.sa/ar/categories/pantry/chocolate-confectionery", "category": "حلويات وشوكولاتة"},
        {"url": "https://panda.sa/ar/categories/beverages/water", "category": "مياه ومشروبات"}
    ]
    print("جاري السحب من أقسام متعددة في بنده...")

    # 3. إعدادات الـ Actor (Playwright Scraper) لتخطي حماية Cloudflare وتنفيذ الجافاسكريبت
    run = client.actor("apify/playwright-scraper").call(run_input={
        "startUrls": target_urls,
        "useChrome": True,
        "pageFunction": r"""
            async function pageFunction(context) {
                const { page, log, request } = context;
                
                log.info('Waiting for Panda search page to load: ' + request.url);
                await page.waitForTimeout(6000); 
                
                // تحديد القسم بناءً على الرابط
                let category = "أخرى";
                if (request.url.includes('%D8%A7%D9%84%D9%85%D8%B1%D8%A7%D8%B9%D9%8A')) category = "ألبان وأجبان";
                else if (request.url.includes('%D8%B4%D9%8A%D8%A8%D8%B3')) category = "تسالي وشيبس";
                else if (request.url.includes('%D8%A8%D9%8A%D8%A8%D8%B3%D9%8A')) category = "مشروبات";

                // النزول لأسفل لتحميل المنتجات
                await page.evaluate(async () => {
                    for(let i=0; i<4; i++) {
                        window.scrollBy(0, window.innerHeight);
                        await new Promise(r => setTimeout(r, 1000));
                    }
                });
                await page.waitForTimeout(3000);
                
                // استخراج المنتجات
                const products = await page.evaluate((cat) => {
                    let items = [];
                    let images = Array.from(document.querySelectorAll('img'));
                    
                    images.forEach(img => {
                        let src = img.getAttribute('data-src') || img.src;
                        if (src && src.startsWith('http') && !src.includes('logo') && !src.includes('icon') && !src.includes('banner')) {
                            if (src.includes('media/catalog') || src.includes('products') || img.width > 60) {
                                let alt_text = img.alt || img.title || '';
                                
                                // --- تحسين الجودة (High Resolution) ---
                                // إزالة _small للحصول على الصورة بدقتها الأصلية العالية
                                let high_res_src = src.replace('_small', '').replace('_medium', '');
                                
                                // --- تحسين اسم المنتج (Improve Product Name) ---
                                // إزالة الوصف الطويل والعلامات مثل -br-- أو النقاط
                                let clean_name = alt_text.split(/-br--|\n|•|<br>|\|/)[0].trim();
                                
                                // إذا كان الاسم فارغاً بعد التنظيف أو قصيراً جداً، نعطيه اسماً افتراضياً بناءً على القسم
                                if(clean_name.length < 3) {
                                    clean_name = "منتج من قسم " + category + " " + Math.floor(Math.random() * 1000);
                                }
                                
                                // اختصار الاسم إذا كان أطول من اللازم (حد أقصى 50 حرف)
                                if (clean_name.length > 50) {
                                    clean_name = clean_name.substring(0, 50) + '...';
                                }

                                // توليد باركود وهمي للعينة لأن بنده لا تعرض الباركود في صفحة البحث
                                let fake_barcode = "628" + Math.floor(100000000 + Math.random() * 900000000);
                                let safe_name = clean_name.replace(/[\/\\\\?%*:|"<>]/g, '-').trim();
                                
                                items.push({ 
                                    name: safe_name, 
                                    image_url: high_res_src,
                                    barcode: fake_barcode,
                                    category: cat
                                });
                            }
                        }
                    });
                    return items;
                }, category);
                
                // تصفية التكرارات
                const uniqueItems = [];
                const seenUrls = new Set();
                for (const item of products) {
                    if (!seenUrls.has(item.image_url)) {
                        seenUrls.add(item.image_url);
                        uniqueItems.push(item);
                    }
                }
                
                log.info('Found ' + uniqueItems.length + ' products on this page');
                return uniqueItems;
            }
        """,
    })

    print("تم الانتهاء من السحب! جاري معالجة وتنزيل العينة...")
    
    csv_file = os.path.join(folder_name, "Products_Database_Sample.csv")
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # تمت إضافة عمود Image Link كما طلب العميل
        writer.writerow(["Barcode", "Product Name", "Category", "Image File Name", "Image Link"])
        
        all_items = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            if type(item) is list:
                all_items.extend(item)
            else:
                all_items.append(item)
                
        downloaded = 0
        for data in all_items:
            img_url = data.get("image_url")
            barcode = data.get("barcode")
            name = data.get("name")
            category = data.get("category")
            
            if img_url and barcode and name:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    if img_response.status_code == 200:
                        file_name = f"{barcode}.jpg"
                        file_path = os.path.join(folder_name, file_name)
                        with open(file_path, 'wb') as img_f:
                            img_f.write(img_response.content)
                        # تسجيل البيانات مع رابط الصورة
                        writer.writerow([barcode, name, category, file_name, img_url])
                        print(f"تم تحميل: {name[:40]}...")
                        downloaded += 1
                except Exception as e:
                    pass

    print(f"\n✅ تمت العملية بنجاح!")
    print(f"تم تحميل {downloaded} منتج مع الصور وملف الإكسل (Products_Database_Sample.csv) في مجلد {folder_name}.")

if __name__ == '__main__':
    generate_pro_sample()
