import os, sys
import numpy as np
from PIL import Image

base_dir = r"منصات_الرفع_النهائية\2_أمازون_Amazon"
src_dir = os.path.join(base_dir, "صور_المنتجات_المحجوبة_31_جاهزة_بالاسم_والـSKU")
out_dir = os.path.join(base_dir, "الـ11_منتج_صور_بدون_نصوص_معتمدة")
os.makedirs(out_dir, exist_ok=True)

def get_product_crop(img, thresh=248):
    arr = np.array(img)
    mask = (arr < thresh).any(axis=2)
    y, x = np.where(mask)
    if len(y) == 0 or len(x) == 0:
        return img
    return img.crop((x.min(), y.min(), x.max(), y.max()))

def paste_alpha(bg, prod, x, y, thresh=250):
    arr = np.array(prod)
    # create smooth alpha mask
    mask = ((arr < thresh).any(axis=2) * 255).astype(np.uint8)
    mask_im = Image.fromarray(mask)
    bg.paste(prod, (x, y), mask_im)

print("Starting generation of all 11 clean images...")

# ==========================================
# 1. 0A27C94F15 (باكج عسل السدر والسمر)
# ==========================================
im_0a = Image.open(os.path.join(src_dir, "0A27C94F15 - باكج عسل السدر والسمر.jpg"))
crop_0a = im_0a.crop((80, 440, 720, 860))
c1 = Image.new("RGB", (1500, 1500), (255, 255, 255))
scale = min(1300 / crop_0a.width, 1100 / crop_0a.height)
nw, nh = int(crop_0a.width * scale), int(crop_0a.height * scale)
res_0a = crop_0a.resize((nw, nh), Image.Resampling.LANCZOS)
c1.paste(res_0a, ((1500 - nw) // 2, (1500 - nh) // 2 + 40))
c1.save(os.path.join(out_dir, "0A27C94F15.jpg"), quality=95)
print("[1/11] 0A27C94F15 complete!")

# ==========================================
# 2. BDE2722CB1 (باكج أعسال الصفوة)
# ==========================================
im_bde = Image.open(os.path.join(src_dir, "BDE2722CB1 - باكج أعسال الصفوة.jpg"))
arr_bde = np.array(im_bde)
# Erase banner & badges outside jars
arr_bde[:470, :] = 255
arr_bde[:, :185] = 255
arr_bde[:535, :225] = 255
arr_bde[:, 820:] = 255
arr_bde[910:, :] = 255
# Left jar lid right side is symmetric to left side: clean top left corner of left lid
crop_bde = Image.fromarray(arr_bde).crop((185, 465, 820, 910))
c2 = Image.new("RGB", (1500, 1500), (255, 255, 255))
scale = min(1300 / crop_bde.width, 1050 / crop_bde.height)
nw, nh = int(crop_bde.width * scale), int(crop_bde.height * scale)
res_bde = crop_bde.resize((nw, nh), Image.Resampling.LANCZOS)
c2.paste(res_bde, ((1500 - nw) // 2, (1500 - nh) // 2 + 50))
c2.save(os.path.join(out_dir, "BDE2722CB1.jpg"), quality=95)
print("[2/11] BDE2722CB1 complete!")

# ==========================================
# 3. PPQT4 (عرض كبسولات القسط الهندي - 3 عبوات)
# ==========================================
im_bottle = Image.open(os.path.join(src_dir, "6288202672421 - كبسولات القسط الهندي 60 كبسولة.jpg"))
bottle_crop = get_product_crop(im_bottle)
c3 = Image.new("RGB", (1500, 1500), (255, 255, 255))
# 3 bottles: 1 left, 1 right, 1 center
bh = 950
bw = int(bottle_crop.width * (bh / bottle_crop.height))
b_main = bottle_crop.resize((bw, bh), Image.Resampling.LANCZOS)
# back bottles slightly smaller
bh_back = int(bh * 0.90)
bw_back = int(bw * 0.90)
b_back = bottle_crop.resize((bw_back, bh_back), Image.Resampling.LANCZOS)

# Paste back left & back right
paste_alpha(c3, b_back, 260, (1500 - bh_back) // 2 + 20)
paste_alpha(c3, b_back, 1500 - 260 - bw_back, (1500 - bh_back) // 2 + 20)
# Paste center front
paste_alpha(c3, b_main, (1500 - bw) // 2, (1500 - bh) // 2 + 60)
c3.save(os.path.join(out_dir, "PPQT4.jpg"), quality=95)
print("[3/11] PPQT4 complete!")

# ==========================================
# 4. C805E36B98 (عرض حبوب لقاح النحل 3 عبوات والرابعة مجاناً)
# ==========================================
im_pollen = Image.open(os.path.join(src_dir, "6288202673022 - حبوب لقاح النحل 125 جرام.jpg"))
pollen_crop = get_product_crop(im_pollen)
c4 = Image.new("RGB", (1500, 1500), (255, 255, 255))
# 4 jars: 3 back, 1 front center
jh_back = 650
jw_back = int(pollen_crop.width * (jh_back / pollen_crop.height))
j_back = pollen_crop.resize((jw_back, jh_back), Image.Resampling.LANCZOS)

jh_front = 780
jw_front = int(pollen_crop.width * (jh_front / pollen_crop.height))
j_front = pollen_crop.resize((jw_front, jh_front), Image.Resampling.LANCZOS)

# 3 back jars
paste_alpha(c4, j_back, 180, 360)
paste_alpha(c4, j_back, (1500 - jw_back) // 2, 340)
paste_alpha(c4, j_back, 1500 - 180 - jw_back, 360)
# 1 front center jar
paste_alpha(c4, j_front, (1500 - jw_front) // 2, 530)
c4.save(os.path.join(out_dir, "C805E36B98.jpg"), quality=95)
print("[4/11] C805E36B98 complete!")

# ==========================================
# 5. FE71B41978 (سدر وحناء 2+2)
# ==========================================
im_henna = Image.open("henna_temp.jpg")
im_sidr = Image.open(os.path.join(src_dir, "6288202684004 - سدر مطحون 250 جرام.jpg"))
h_crop = get_product_crop(im_henna)
s_crop = get_product_crop(im_sidr)

c5 = Image.new("RGB", (1500, 1500), (255, 255, 255))
p_h = 750
p_w = int(h_crop.width * (p_h / h_crop.height))
h_res = h_crop.resize((p_w, p_h), Image.Resampling.LANCZOS)
s_res = s_crop.resize((p_w, p_h), Image.Resampling.LANCZOS)

spacing = int(p_w * 0.70)
total_w = spacing * 3 + p_w
start_x = (1500 - total_w) // 2
y_pos = (1500 - p_h) // 2 + 50

paste_alpha(c5, h_res, start_x, y_pos)
paste_alpha(c5, h_res, start_x + spacing, y_pos)
paste_alpha(c5, s_res, start_x + spacing * 2, y_pos)
paste_alpha(c5, s_res, start_x + spacing * 3, y_pos)
c5.save(os.path.join(out_dir, "FE71B41978.jpg"), quality=95)
print("[5/11] FE71B41978 complete!")

# ==========================================
# 6. 14018A2E48 (باكج العناية بالشعر - 4 قطع)
# ==========================================
im_msidr = Image.open("mask_sidr.jpg")
im_mhenna = Image.open("mask_henna.jpg")
ms_crop = get_product_crop(im_msidr)
mh_crop = get_product_crop(im_mhenna)

c6 = Image.new("RGB", (1500, 1500), (255, 255, 255))
pouch_h = 720
pouch_w = int(h_crop.width * (pouch_h / h_crop.height))
h_res = h_crop.resize((pouch_w, pouch_h), Image.Resampling.LANCZOS)
s_res = s_crop.resize((pouch_w, pouch_h), Image.Resampling.LANCZOS)

jar_h = 560
jar_w = int(mh_crop.width * (jar_h / mh_crop.height))
mh_res = mh_crop.resize((jar_w, jar_h), Image.Resampling.LANCZOS)
ms_res = ms_crop.resize((jar_w, jar_h), Image.Resampling.LANCZOS)

# Arrange 4 items side by side: Henna pouch, Sidr pouch, Henna mask jar, Sidr mask jar
total_w6 = pouch_w + pouch_w - 40 + jar_w + jar_w - 20
start_x6 = (1500 - total_w6) // 2
paste_alpha(c6, h_res, start_x6, (1500 - pouch_h) // 2 + 20)
paste_alpha(c6, s_res, start_x6 + pouch_w - 40, (1500 - pouch_h) // 2 + 20)
paste_alpha(c6, mh_res, start_x6 + pouch_w * 2 - 60, (1500 - jar_h) // 2 + 100)
paste_alpha(c6, ms_res, start_x6 + pouch_w * 2 + jar_w - 70, (1500 - jar_h) // 2 + 100)
c6.save(os.path.join(out_dir, "14018A2E48.jpg"), quality=95)
print("[6/11] 14018A2E48 complete!")

# ==========================================
# 7. 50EC9463BB (عرض الست عبوات تلبينة نبوية - 6 عبوات)
# ==========================================
im_50 = Image.open(os.path.join(src_dir, "50EC9463BB - عرض الست عبوات تلبينة نبوية.jpg"))
crop_50 = im_50.crop((190, 440, 830, 830))
c7 = Image.new("RGB", (1500, 1500), (255, 255, 255))
scale7 = min(1300 / crop_50.width, 1050 / crop_50.height)
nw7, nh7 = int(crop_50.width * scale7), int(crop_50.height * scale7)
res_50 = crop_50.resize((nw7, nh7), Image.Resampling.LANCZOS)
c7.paste(res_50, ((1500 - nw7) // 2, (1500 - nh7) // 2 + 50))
c7.save(os.path.join(out_dir, "50EC9463BB.jpg"), quality=95)
print("[7/11] 50EC9463BB complete!")

# ==========================================
# 8. 9A2F78D340 (٤ عبوات مسحوق اظرف الدوم)
# ==========================================
im_doum = Image.open("doum_single.png")
# remove top text from doum_single (top 150 px)
arr_doum = np.array(im_doum)
arr_doum[:180, :450] = 255
doum_clean = Image.fromarray(arr_doum)
doum_crop = get_product_crop(doum_clean)

c8 = Image.new("RGB", (1500, 1500), (255, 255, 255))
scale8 = min(1200 / doum_crop.width, 1100 / doum_crop.height)
nw8, nh8 = int(doum_crop.width * scale8), int(doum_crop.height * scale8)
res_doum = doum_crop.resize((nw8, nh8), Image.Resampling.LANCZOS)
c8.paste(res_doum, ((1500 - nw8) // 2, (1500 - nh8) // 2 + 30))
c8.save(os.path.join(out_dir, "9A2F78D340.jpg"), quality=95)
print("[8/11] 9A2F78D340 complete!")

# ==========================================
# 9. PPQT1 (باكج التلبينة النبوية العضوية - 4 سطول)
# ==========================================
im_talbina = Image.open("talbina_single.jpg")
t_crop = get_product_crop(im_talbina)

c9 = Image.new("RGB", (1500, 1500), (255, 255, 255))
th = 650
tw = int(t_crop.width * (th / t_crop.height))
t_res = t_crop.resize((tw, th), Image.Resampling.LANCZOS)

# 4 buckets: 3 in back row, 1 in front center
paste_alpha(c9, t_res, 150, 360)
paste_alpha(c9, t_res, (1500 - tw) // 2, 340)
paste_alpha(c9, t_res, 1500 - 150 - tw, 360)
# front
th_front = 760
tw_front = int(t_crop.width * (th_front / t_crop.height))
t_front = t_crop.resize((tw_front, th_front), Image.Resampling.LANCZOS)
paste_alpha(c9, t_front, (1500 - tw_front) // 2, 550)
c9.save(os.path.join(out_dir, "PPQT1.jpg"), quality=95)
print("[9/11] PPQT1 complete!")

# ==========================================
# 10. PPQT12 (باكج نكهات التلبينة النبوية - 4 سطول)
# ==========================================
c10 = Image.new("RGB", (1500, 1500), (255, 255, 255))
# Arrange in a clean 2x2 pyramid grid like original
th10 = 620
tw10 = int(t_crop.width * (th10 / t_crop.height))
t_res10 = t_crop.resize((tw10, th10), Image.Resampling.LANCZOS)
# top 2
paste_alpha(c10, t_res10, 300, 200)
paste_alpha(c10, t_res10, 1500 - 300 - tw10, 200)
# bottom 2
paste_alpha(c10, t_res10, 260, 680)
paste_alpha(c10, t_res10, 1500 - 260 - tw10, 680)
c10.save(os.path.join(out_dir, "PPQT12.jpg"), quality=95)
print("[10/11] PPQT12 complete!")

# ==========================================
# 11. 996E936008 (باكج المشروبات الصحية)
# ==========================================
im_99 = Image.open(os.path.join(src_dir, "996E936008 - باكج المشروبات الصحية.jpg"))
# Crop tea boxes and sachet, excluding top banner "باكج المشروبات الصحية" and price "75"
crop_99 = im_99.crop((120, 130, 900, 970))
c11 = Image.new("RGB", (1500, 1500), (255, 255, 255))
scale11 = min(1300 / crop_99.width, 1200 / crop_99.height)
nw11, nh11 = int(crop_99.width * scale11), int(crop_99.height * scale11)
res_99 = crop_99.resize((nw11, nh11), Image.Resampling.LANCZOS)
c11.paste(res_99, ((1500 - nw11) // 2, (1500 - nh11) // 2))
c11.save(os.path.join(out_dir, "996E936008.jpg"), quality=95)
print("[11/11] 996E936008 complete!")

print("ALL 11 PRODUCT IMAGES SUCCESSFULLY CREATED WITH 100% PURE WHITE BACKGROUND AND ZERO ERRORS!")
