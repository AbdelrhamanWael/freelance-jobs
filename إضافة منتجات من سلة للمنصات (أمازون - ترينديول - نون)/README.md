# اضافة منتجات من سلة للمنصات (امازون - ترينديول - نون)

## هيكل المشروع

```
.
|-- data/
|   |-- raw/            <- ضع هنا ملف تصدير سلة (.xlsx او .csv)
|   `-- clean/          <- المخرجات التلقائية بعد التشغيل
|-- day1_prepare_data/
|   |-- config.py       <- *** عدل هذا الملف اولا ***
|   |-- step1_load_raw.py
|   |-- step2_filter_active.py
|   |-- step3_split_platforms.py
|   `-- run_all.py      <- تشغيل اليوم الاول كاملا
|-- logs/
|   `-- day1.log
`-- requirements.txt
```

## التشغيل السريع (اليوم الاول)

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. تصدير المنتجات من سلة
- لوحة تحكم سلة -> المنتجات -> تصدير المنتجات
- احفظ الملف في:  `data/raw/salla_products_export.xlsx`

### 3. ضبط اسماء الاعمدة
- افتح `day1_prepare_data/config.py`
- تاكد ان المفاتيح في `COL_MAP` تطابق اسماء الاعمدة الفعلية في ملف سلة
- تاكد من قيمة `ACTIVE_STATUS_VALUES` (نشط / active / ...)

### 4. التشغيل
```bash
python day1_prepare_data/run_all.py
```

### المخرجات
| الملف | المحتوى |
|---|---|
| `data/clean/salla_active_products.csv` | جميع المنتجات النشطة المنظفة |
| `data/clean/amazon_ready.csv` | نسخة جاهزة لمطابقة امازون |
| `data/clean/noon_ready.csv` | نسخة جاهزة لمطابقة نون |
| `data/clean/trendyol_ready.csv` | نسخة جاهزة لمطابقة ترينديول |
| `data/clean/excluded_products.csv` | المنتجات المستبعدة (مخفية/بلا SKU) |
| `logs/day1.log` | سجل تفصيلي لكل خطوة |
