import asyncio
import re
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_riyadh_activities():
    # 1. قائمة الكلمات البحثية الشاملة للرياض
    search_queries = [
        "Padel courts Riyadh",
        "Bowling centers Riyadh",
        "Billiards club Riyadh",
        "Padel Al Malqa",  # البحث بالأحياء لزيادة عدد النتائج
        "Bowling Hittin Riyadh"
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # خليه False عشان تتابع العملية
        context = await browser.new_context()
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        all_data = []
        seen_names = set() # لمنع التكرار

        for query in search_queries:
            print(f"--- جاري البحث عن: {query} ---")
            await page.goto(f"https://www.google.com/maps/search/{query}")
            await page.wait_for_timeout(5000) # انتظار تحميل النتائج

            # سكرول في القائمة الجانبية لتحميل كل الأماكن
            for _ in range(5): # عدد مرات السكرول
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(2)

            # استخراج الروابط (Links) الخاصة بكل مكان
            locations = await page.query_selector_all('a.hfpxzc')
            
            for loc in locations:
                name = await loc.get_attribute('aria-label')
                if name in seen_names: continue
                
                link = await loc.get_attribute('href')
                
                # استخراج الإحداثيات من الـ URL باستخدام Regex
                # بيبحث عن نمط @24.713,46.675
                coord_match = re.search(r'@([-]?\d+\.\d+),([-]?\d+\.\d+)', link)
                lat = coord_match.group(1) if coord_match else "N/A"
                lng = coord_match.group(2) if coord_match else "N/A"

                place_info = {
                    "place_name": name,
                    "google_maps_short_link": link, # تقدر تعمل له Shorten لاحقاً
                    "coordinates": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "category": query # عشان تعرف المكان ده تبع أنهي نشاط
                }
                
                all_data.append(place_info)
                seen_names.add(name)
                
                if len(all_data) >= 200: # التوقف عند الوصول للعدد المطلوب
                    break
            
            if len(all_data) >= 200: break

        # 2. حفظ البيانات في ملف JSON النهائي
        with open('riyadh_leisure_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        print(f"تم الانتهاء! تم جمع {len(all_data)} مكان وحفظهم في riyadh_leisure_data.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_riyadh_activities())