import yt_dlp
import pandas as pd
import os

files_to_process = [
    {
        'excel_file': 'Reels_Chinese_Embassy.xlsx',
        'folder_name': 'Chinese_Embassy_Reels',
        'prefix': 'Reel_'
    },
    {
        'excel_file': 'Reels_US_Embassy.xlsx',
        'folder_name': 'US_Embassy_Reels',
        'prefix': 'Reel_'
    },
    {
        'excel_file': 'Excluded_Posts_31.xlsx',
        'folder_name': 'Excluded_Posts_Media',
        'prefix': 'Media_'
    }
]

for item in files_to_process:
    excel_file = item['excel_file']
    folder_name = item['folder_name']
    file_prefix = item.get('prefix', 'Reel_')
    
    # 1. إنشاء مجلد خاص بكل صفحة
    os.makedirs(folder_name, exist_ok=True)
    
    # 2. قراءة الروابط من ملف الإكسيل
    print(f"جاري قراءة الملف: {excel_file}...")
    try:
        df = pd.read_excel(excel_file)
        if 'Post URL' in df.columns:
            # استخراج الروابط وتجاهل الخلايا الفارغة
            urls = df['Post URL'].dropna().tolist()
            print(f"تم العثور على {len(urls)} رابط في {excel_file}.")
        else:
            print(f"لم يتم العثور على عمود 'Post URL' في {excel_file}. سيتم التخطي.")
            continue
    except Exception as e:
        print(f"حدث خطأ أثناء قراءة {excel_file}: {e}")
        continue
    
    # 3. إعدادات التحميل
    ydl_opts = {
        # تسمية الملفات بالترتيب داخل المجلد
        'outtmpl': f'{folder_name}/{file_prefix}%(autonumber)03d.%(ext)s', 
        # اختيار أفضل جودة بصيغة mp4
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # تجاهل الأخطاء
        'ignoreerrors': True, 
    }
    
    # 4. بدء التحميل
    print(f"جاري بدء التحميل لمجلد {folder_name}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
        
    print(f"تم تحميل فيديوهات {folder_name} بنجاح!\n")

print("تم الانتهاء من تحميل جميع الفيديوهات!")