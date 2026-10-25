import os, sys
from PIL import Image
from rembg import remove

src_dir = r"منصات_الرفع_النهائية\2_أمازون_Amazon\صور_المنتجات_المحجوبة_31_جاهزة_بالاسم_والـSKU"
out_dir = r"منصات_الرفع_النهائية\2_أمازون_Amazon\الـ11_منتج_صور_بدون_نصوص_معتمدة"
os.makedirs(out_dir, exist_ok=True)

# List of the 11 items and custom crop / processing rules
items = [
    {
        "sku": "0A27C94F15",
        "file": "0A27C94F15 - باكج عسل السدر والسمر.jpg",
        "crop_box": (100, 440, 710, 860),  # Keep jars and pouch, exclude banner, logo & footer
        "target_scale": 0.85
    },
    {
        "sku": "BDE2722CB1",
        "file": "BDE2722CB1 - باكج أعسال الصفوة.jpg",
        "crop_box": (170, 460, 830, 890),  # Keep 2 jars, exclude banner and badge
        "target_scale": 0.85
    },
    {
        "sku": "14018A2E48",
        "file": "14018A2E48 - باكج العناية بالشعر.jpg",
        "crop_box": (120, 440, 920, 860),  # Keep 4 products, exclude top banner and badge
        "target_scale": 0.88
    },
    {
        "sku": "50EC9463BB",
        "file": "50EC9463BB - عرض الست عبوات تلبينة نبوية.jpg",
        "crop_box": (190, 410, 820, 825),  # Keep 6 pouches, exclude banner and badge
        "target_scale": 0.85
    },
    {
        "sku": "FE71B41978",
        "file": "FE71B41978 - سدر وحناء (٢+٢).jpg",
        "crop_box": (90, 400, 930, 755),   # Keep 4 pouches, exclude banner and badge
        "target_scale": 0.88
    },
    {
        "sku": "9A2F78D340",
        "file": "9A2F78D340 - ٤ عبوات مسحوق اظرف الدوم.jpg",
        "crop_box": (120, 390, 920, 985),  # Keep 4 boxes & sachets, exclude top banner & badge
        "target_scale": 0.88
    },
    {
        "sku": "C805E36B98",
        "file": "C805E36B98 - عرض حبوب لقاح النحل ٣ عبوات والرابعة مجا.jpg",
        "crop_box": (120, 430, 880, 880),  # Keep 4 pollen jars, exclude banner and badge
        "target_scale": 0.85
    },
    {
        "sku": "PPQT1",
        "file": "PPQT1 - باكج التلبينة النبوية العضوية.jpg",
        "crop_box": (110, 400, 870, 920),  # Keep 4 buckets, exclude banner and badge
        "target_scale": 0.85
    },
    {
        "sku": "PPQT12",
        "file": "PPQT12 - باكج نكهات التلبينة النبوية.jpg",
        "crop_box": (190, 330, 810, 940),  # Keep 4 buckets, exclude banner and badge
        "target_scale": 0.85
    },
    {
        "sku": "PPQT4",
        "file": "PPQT4 - عرض كبسولات القسط الهندي.jpg",
        "crop_box": (240, 460, 755, 830),  # Keep 3 bottles, exclude banner, text & background
        "target_scale": 0.85
    },
    {
        "sku": "996E936008",
        "file": "996E936008 - باكج المشروبات الصحية.jpg",
        "crop_box": (160, 130, 890, 970),  # Keep tea boxes and pouch, remove banner
        "target_scale": 0.85
    }
]

for item in items:
    sku = item["sku"]
    fn = item["file"]
    p = os.path.join(src_dir, fn)
    if not os.path.exists(p):
        print(f"Missing file for {sku}: {p}")
        continue
    
    img = Image.open(p)
    crop = img.crop(item["crop_box"])
    
    # Run rembg to remove any surrounding artifacts or background
    isolated = remove(crop)
    
    # Create pure white canvas
    canvas = Image.new("RGB", (1500, 1500), (255, 255, 255))
    cw, ch = isolated.size
    max_dim = int(1500 * item["target_scale"])
    scale = min(max_dim / cw, max_dim / ch)
    nw, nh = int(cw * scale), int(ch * scale)
    
    resized = isolated.resize((nw, nh), Image.Resampling.LANCZOS)
    
    # Paste centered
    ox = (1500 - nw) // 2
    oy = (1500 - nh) // 2
    canvas.paste(resized, (ox, oy), resized)
    
    # Save both by SKU and descriptive name
    out_sku = os.path.join(out_dir, f"{sku}.jpg")
    out_desc = os.path.join(out_dir, f"{sku} - {fn.split(' - ')[1] if ' - ' in fn else fn}")
    if not out_desc.endswith(".jpg"):
        out_desc += ".jpg"
        
    canvas.save(out_sku, quality=95)
    canvas.save(out_desc, quality=95)
    print(f"Successfully processed and saved {sku}")

print("ALL 11 IMAGES PROCESSED SUCCESSFULLY!")
