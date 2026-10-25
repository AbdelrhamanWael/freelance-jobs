import os, shutil, sys, openpyxl
sys.stdout.reconfigure(encoding='utf-8')

clean_dir = 'منصات_الرفع_النهائية/2_أمازون_Amazon/صور_المنتجات_المحجوبة_أمازون_31_خلفية_بيضاء_جاهزة'
named_dir = 'منصات_الرفع_النهائية/2_أمازون_Amazon/صور_المنتجات_المحجوبة_31_جاهزة_بالاسم_والـSKU'
os.makedirs(named_dir, exist_ok=True)

wb = openpyxl.load_workbook('qitafaltabiea_13-09-2026-01-48_OZjH2K61peroLtoTcf55nd6F8O8zBkXe1ubO1qRS_products.xlsx', data_only=True)
ws = wb.active

sku_names = {}
for r in range(3, ws.max_row+1):
    sku = str(ws.cell(r, 11).value).strip() if ws.cell(r, 11).value is not None else ''
    name = str(ws.cell(r, 3).value).strip() if ws.cell(r, 3).value is not None else ''
    if sku:
        sku_names[sku] = name

forbidden = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
for f in os.listdir(clean_dir):
    sku = os.path.splitext(f)[0]
    pname = sku_names.get(sku, 'منتج')
    clean_pname = ''.join(c for c in pname if c not in forbidden).strip()[:40]
    new_name = f"{sku} - {clean_pname}.jpg"
    shutil.copy(os.path.join(clean_dir, f), os.path.join(named_dir, new_name))

print(f"Created {len(os.listdir(named_dir))} renamed images in: {named_dir}")
