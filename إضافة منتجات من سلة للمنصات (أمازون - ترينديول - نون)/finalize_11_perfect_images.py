import os, sys
import numpy as np
from PIL import Image

out_dir = r"منصات_الرفع_النهائية\2_أمازون_Amazon\الـ11_منتج_صور_بدون_نصوص_معتمدة"
src_dir = r"منصات_الرفع_النهائية\2_أمازون_Amazon\صور_المنتجات_المحجوبة_31_جاهزة_بالاسم_والـSKU"
os.makedirs(out_dir, exist_ok=True)

def paste_rgba(canvas, img, x, y):
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    canvas.paste(img, (x, y), img)

print("Starting final assembly of all 11 perfect images...")

# 1. 0A27C94F15 (باكج عسل السدر والسمر)
im_0a = Image.open(os.path.join(src_dir, "0A27C94F15 - باكج عسل السدر والسمر.jpg"))
crop_0a = im_0a.crop((80, 440, 720, 860))
c1 = Image.new("RGB", (1500, 1500), (255, 255, 255))
s1 = min(1300 / crop_0a.width, 1100 / crop_0a.height)
nw1, nh1 = int(crop_0a.width * s1), int(crop_0a.height * s1)
c1.paste(crop_0a.resize((nw1, nh1), Image.Resampling.LANCZOS), ((1500 - nw1) // 2, (1500 - nh1) // 2 + 40))
c1.save(os.path.join(out_dir, "0A27C94F15.jpg"), quality=95)
print("[1/11] 0A27C94F15 done")

# 2. BDE2722CB1 (باكج أعسال الصفوة)
im_bde = Image.open(os.path.join(src_dir, "BDE2722CB1 - باكج أعسال الصفوة.jpg"))
arr_bde = np.array(im_bde)
# Erase all text, banner and green badge
arr_bde[:470, :] = 255
arr_bde[:, :200] = 255
arr_bde[:535, :245] = 255
arr_bde[:, 820:] = 255
arr_bde[910:, :] = 255
# clean any remaining green pixels around left lid
for y in range(465, 535):
    for x in range(200, 260):
        r, g, b = [int(v) for v in arr_bde[y, x]]
        if g > 90 and g > r + 10:
            arr_bde[y, x] = [255, 255, 255]
crop_bde = Image.fromarray(arr_bde).crop((195, 465, 820, 910))
c2 = Image.new("RGB", (1500, 1500), (255, 255, 255))
s2 = min(1300 / crop_bde.width, 1050 / crop_bde.height)
nw2, nh2 = int(crop_bde.width * s2), int(crop_bde.height * s2)
c2.paste(crop_bde.resize((nw2, nh2), Image.Resampling.LANCZOS), ((1500 - nw2) // 2, (1500 - nh2) // 2 + 50))
c2.save(os.path.join(out_dir, "BDE2722CB1.jpg"), quality=95)
print("[2/11] BDE2722CB1 done")

# 3. PPQT4 (عرض كبسولات القسط الهندي - 3 عبوات)
if os.path.exists("bottle_isolated.png"):
    bot = Image.open("bottle_isolated.png")
    c3 = Image.new("RGBA", (1500, 1500), (255, 255, 255, 255))
    bh = 850
    bw = int(bot.width * (bh / bot.height))
    b_main = bot.resize((bw, bh), Image.Resampling.LANCZOS)
    
    bh_b = int(bh * 0.88)
    bw_b = int(bw * 0.88)
    b_back = bot.resize((bw_b, bh_b), Image.Resampling.LANCZOS)
    
    paste_rgba(c3, b_back, 240, (1500 - bh_b) // 2 - 20)
    paste_rgba(c3, b_back, 1500 - 240 - bw_b, (1500 - bh_b) // 2 - 20)
    paste_rgba(c3, b_main, (1500 - bw) // 2, (1500 - bh) // 2 + 60)
    c3.convert("RGB").save(os.path.join(out_dir, "PPQT4.jpg"), quality=95)
    print("[3/11] PPQT4 done")

# 4. C805E36B98 (عرض حبوب لقاح النحل - 4 عبوات)
if os.path.exists("pollen_isolated.png"):
    pol = Image.open("pollen_isolated.png")
    c4 = Image.new("RGBA", (1500, 1500), (255, 255, 255, 255))
    jh_b = 640
    jw_b = int(pol.width * (jh_b / pol.height))
    j_b = pol.resize((jw_b, jh_b), Image.Resampling.LANCZOS)
    
    jh_f = 780
    jw_f = int(pol.width * (jh_f / pol.height))
    j_f = pol.resize((jw_f, jh_f), Image.Resampling.LANCZOS)
    
    # 3 in back
    paste_rgba(c4, j_b, 160, 320)
    paste_rgba(c4, j_b, (1500 - jw_b) // 2, 300)
    paste_rgba(c4, j_b, 1500 - 160 - jw_b, 320)
    # 1 in front
    paste_rgba(c4, j_f, (1500 - jw_f) // 2, 520)
    c4.convert("RGB").save(os.path.join(out_dir, "C805E36B98.jpg"), quality=95)
    print("[4/11] C805E36B98 done")

# 5. FE71B41978 (سدر وحناء 2+2)
if os.path.exists("henna_isolated.png") and os.path.exists("sidr_isolated.png"):
    h_iso = Image.open("henna_isolated.png")
    s_iso = Image.open("sidr_isolated.png")
    c5 = Image.new("RGBA", (1500, 1500), (255, 255, 255, 255))
    ph = 760
    pw = int(h_iso.width * (ph / h_iso.height))
    h_r = h_iso.resize((pw, ph), Image.Resampling.LANCZOS)
    s_r = s_iso.resize((pw, ph), Image.Resampling.LANCZOS)
    
    sp = int(pw * 0.65)
    tot_w = sp * 3 + pw
    sx = (1500 - tot_w) // 2
    sy = (1500 - ph) // 2 + 50
    paste_rgba(c5, h_r, sx, sy)
    paste_rgba(c5, h_r, sx + sp, sy)
    paste_rgba(c5, s_r, sx + sp * 2, sy)
    paste_rgba(c5, s_r, sx + sp * 3, sy)
    c5.convert("RGB").save(os.path.join(out_dir, "FE71B41978.jpg"), quality=95)
    print("[5/11] FE71B41978 done")

# 6. 14018A2E48 (باكج العناية بالشعر - 4 قطع)
if os.path.exists("mask_henna_isolated.png") and os.path.exists("mask_sidr_isolated.png"):
    mh_iso = Image.open("mask_henna_isolated.png")
    ms_iso = Image.open("mask_sidr_isolated.png")
    c6 = Image.new("RGBA", (1500, 1500), (255, 255, 255, 255))
    
    pouch_h = 700
    pouch_w = int(h_iso.width * (pouch_h / h_iso.height))
    h_r6 = h_iso.resize((pouch_w, pouch_h), Image.Resampling.LANCZOS)
    s_r6 = s_iso.resize((pouch_w, pouch_h), Image.Resampling.LANCZOS)
    
    jar_h = 530
    jar_w = int(mh_iso.width * (jar_h / mh_iso.height))
    mh_r6 = mh_iso.resize((jar_w, jar_h), Image.Resampling.LANCZOS)
    ms_r6 = ms_iso.resize((jar_w, jar_h), Image.Resampling.LANCZOS)
    
    # Arrange 4 items: Henna pouch, Sidr pouch, Henna mask jar, Sidr mask jar
    tot_w6 = pouch_w * 2 - 30 + jar_w * 2 - 20
    sx6 = (1500 - tot_w6) // 2
    paste_rgba(c6, h_r6, sx6, (1500 - pouch_h) // 2)
    paste_rgba(c6, s_r6, sx6 + pouch_w - 30, (1500 - pouch_h) // 2)
    paste_rgba(c6, mh_r6, sx6 + pouch_w * 2 - 40, (1500 - jar_h) // 2 + 85)
    paste_rgba(c6, ms_r6, sx6 + pouch_w * 2 + jar_w - 50, (1500 - jar_h) // 2 + 85)
    c6.convert("RGB").save(os.path.join(out_dir, "14018A2E48.jpg"), quality=95)
    print("[6/11] 14018A2E48 done")

# 7. 50EC9463BB (عرض الست عبوات تلبينة نبوية - 6 عبوات)
im_50 = Image.open(os.path.join(src_dir, "50EC9463BB - عرض الست عبوات تلبينة نبوية.jpg"))
arr_50 = np.array(im_50)
# erase badge and top banner completely
arr_50[:450, :] = 255
arr_50[:, :210] = 255
arr_50[:500, :240] = 255
crop_50 = Image.fromarray(arr_50).crop((190, 445, 830, 830))
c7 = Image.new("RGB", (1500, 1500), (255, 255, 255))
s7 = min(1300 / crop_50.width, 1050 / crop_50.height)
nw7, nh7 = int(crop_50.width * s7), int(crop_50.height * s7)
c7.paste(crop_50.resize((nw7, nh7), Image.Resampling.LANCZOS), ((1500 - nw7) // 2, (1500 - nh7) // 2 + 50))
c7.save(os.path.join(out_dir, "50EC9463BB.jpg"), quality=95)
print("[7/11] 50EC9463BB done")

# 8. 9A2F78D340 (٤ عبوات مسحوق اظرف الدوم)
im_doum = Image.open("doum_single.png")
arr_doum = np.array(im_doum)
arr_doum[:250, :450] = 255
doum_clean = Image.fromarray(arr_doum).crop((90, 240, 920, 850))
c8 = Image.new("RGB", (1500, 1500), (255, 255, 255))
s8 = min(1250 / doum_clean.width, 1100 / doum_clean.height)
nw8, nh8 = int(doum_clean.width * s8), int(doum_clean.height * s8)
c8.paste(doum_clean.resize((nw8, nh8), Image.Resampling.LANCZOS), ((1500 - nw8) // 2, (1500 - nh8) // 2 + 40))
c8.save(os.path.join(out_dir, "9A2F78D340.jpg"), quality=95)
print("[8/11] 9A2F78D340 done")

# 9. PPQT1 (باكج التلبينة النبوية العضوية - 4 سطول)
if os.path.exists("talbina_isolated.png"):
    tal = Image.open("talbina_isolated.png")
    c9 = Image.new("RGBA", (1500, 1500), (255, 255, 255, 255))
    th = 650
    tw = int(tal.width * (th / tal.height))
    t_b = tal.resize((tw, th), Image.Resampling.LANCZOS)
    
    th_f = 780
    tw_f = int(tal.width * (th_f / tal.height))
    t_f = tal.resize((tw_f, th_f), Image.Resampling.LANCZOS)
    
    paste_rgba(c9, t_b, 130, 310)
    paste_rgba(c9, t_b, (1500 - tw) // 2, 290)
    paste_rgba(c9, t_b, 1500 - 130 - tw, 310)
    paste_rgba(c9, t_f, (1500 - tw_f) // 2, 510)
    c9.convert("RGB").save(os.path.join(out_dir, "PPQT1.jpg"), quality=95)
    print("[9/11] PPQT1 done")

# 10. PPQT12 (باكج نكهات التلبينة النبوية - 4 سطول)
if os.path.exists("talbina_isolated.png"):
    c10 = Image.new("RGBA", (1500, 1500), (255, 255, 255, 255))
    th10 = 620
    tw10 = int(tal.width * (th10 / tal.height))
    t10 = tal.resize((tw10, th10), Image.Resampling.LANCZOS)
    
    paste_rgba(c10, t10, 280, 180)
    paste_rgba(c10, t10, 1500 - 280 - tw10, 180)
    paste_rgba(c10, t10, 240, 680)
    paste_rgba(c10, t10, 1500 - 240 - tw10, 680)
    c10.convert("RGB").save(os.path.join(out_dir, "PPQT12.jpg"), quality=95)
    print("[10/11] PPQT12 done")

# 11. 996E936008 (باكج المشروبات الصحية)
im_99 = Image.open(os.path.join(src_dir, "996E936008 - باكج المشروبات الصحية.jpg"))
crop_99 = im_99.crop((120, 130, 900, 970))
c11 = Image.new("RGB", (1500, 1500), (255, 255, 255))
s11 = min(1300 / crop_99.width, 1200 / crop_99.height)
nw11, nh11 = int(crop_99.width * s11), int(crop_99.height * s11)
c11.paste(crop_99.resize((nw11, nh11), Image.Resampling.LANCZOS), ((1500 - nw11) // 2, (1500 - nh11) // 2))
c11.save(os.path.join(out_dir, "996E936008.jpg"), quality=95)
print("[11/11] 996E936008 done")

print("ALL 11 IMAGES FINALIZED PERFECTLY!")
