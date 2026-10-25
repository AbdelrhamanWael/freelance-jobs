import pandas as pd
import numpy as np
from datetime import timedelta

# 1. تحميل البيانات الأصلية كمرجع إحصائي
seed_df = pd.read_csv('saudi_supply_chain_dataset.csv')

# عدد السجلات المطلوب توليدها للعينة
num_records = 10000

# 2. توليد بيانات عشوائية مبنية على توزيع البيانات الأصلية
# نختار سجلات عشوائية من الأصل لنكرر أنماطها
new_data = seed_df.sample(n=num_records, replace=True).reset_index(drop=True)

# 3. إضافة الحقول الجديدة المطلوبة من العميل
carriers = ['Aramex', 'SMSA Express', 'Saudi Post (SPL)', 'DHL Saudi', 'Zajil']

# أ. إضافة اسم شركة الشحن (Carrier) بناءً على نمط النقل
def assign_carrier(mode):
    if mode == 'Air': return 'DHL Saudi'
    if mode == 'Sea': return 'Saudi Post (SPL)'
    return np.random.choice(['Aramex', 'SMSA Express', 'Zajil'])

new_data['carrier'] = new_data['transport_mode'].apply(assign_carrier)

# ب. إضافة جهة المصدر وتصنيفها (Source Type & Platforms)
# 1. تحديد نوع المصدر: متجر إلكتروني، مشغل لوجستي، أو شركة نقل
source_types = ['E-commerce Store', 'Fulfillment / Operator', 'Carrier / Shipping Provider']
new_data['source_type'] = np.random.choice(source_types, size=num_records, p=[0.5, 0.2, 0.3])

# 2. اضافة المنصة للمتجر أو المزود بناءً على نوع المصدر
ecommerce_platforms = ['Salla', 'Zid', 'Shopify', 'Magento', 'Custom Native App']
fulfillment_providers = ['Salasa', 'Snaq', 'Sallat', 'Wared', 'Raqem']
carrier_providers = ['SPL', 'SMSA', 'Aramex', 'Naqel', 'DHL', 'iMile', 'Zajil']

def assign_platform_provider(row):
    stype = row['source_type']
    if stype == 'E-commerce Store':
        return np.random.choice(ecommerce_platforms), np.nan
    elif stype == 'Fulfillment / Operator':
        return np.nan, np.random.choice(fulfillment_providers)
    else: # Carrier
        # إذا كان المصدر شركة نقل، نجعل Provider هو نفس العامل الناقل أو نختار من القائمة
        return np.nan, row['carrier'] if pd.notna(row['carrier']) else np.random.choice(carrier_providers)

# تطبيق الدالة وتوزيع القيم في عمودين
new_data[['source_platform', 'source_provider']] = new_data.apply(assign_platform_provider, axis=1, result_type='expand')


# ج. إضافة رقم التتبع (Tracking Number) بصيغة سعودية
new_data['tracking_number'] = ['SA' + str(np.random.randint(100000000, 999999999)) for _ in range(num_records)]

# ج. إضافة الجداول الزمنية وتفاصيلها الممتدة
new_data['date'] = pd.to_datetime(new_data['date'])
# تاريخ التسليم الموعود (Promised Delivery Date) = تاريخ الطلب + 3 إلى 5 أيام
new_data['promised_delivery_date'] = new_data['date'] + pd.to_timedelta(np.random.randint(3, 6, size=num_records), unit='D')

# جاهزية الشحنة (Ready for pickup) بعد الطلب بـ 6 إلى 12 ساعة
new_data['ready_for_pickup_at'] = new_data['date'] + pd.to_timedelta(np.random.randint(6, 12, size=num_records), unit='h')

# وقت الاستلام من قبل المندوب (Picked up) بعد الجاهزية بـ 4 إلى 12 ساعة
new_data['picked_up_at'] = new_data['ready_for_pickup_at'] + pd.to_timedelta(np.random.randint(4, 12, size=num_records), unit='h')

# وقت خروج الشحنة بين المدن (Shipped)
new_data['shipped_at'] = new_data['picked_up_at'] + pd.to_timedelta(np.random.randint(2, 6, size=num_records), unit='h')

# وقت التسليم النهائي بناءً على Lead Time الموجود في الداتا الأصلية
new_data['delivered_at'] = new_data['shipped_at'] + pd.to_timedelta(new_data['lead_time_days'], unit='D')

# الخروج للتوصيل (Out for delivery) في يوم التسليم قبل 2 إلى 8 ساعات
new_data['out_for_delivery_at'] = new_data['delivered_at'] - pd.to_timedelta(np.random.randint(2, 8, size=num_records), unit='h')


# د. الأبعاد، الوزن الحجمي، والوزن المحاسب
new_data['length_cm'] = np.random.uniform(10, 100, size=num_records).round(1)
new_data['width_cm'] = np.random.uniform(10, 80, size=num_records).round(1)
new_data['height_cm'] = np.random.uniform(5, 60, size=num_records).round(1)
# الوزن الحجمي (Volumetric weight) بقسمة الأبعاد على 4000
new_data['volumetric_weight_kg'] = ((new_data['length_cm'] * new_data['width_cm'] * new_data['height_cm']) / 4000).round(2)

new_data['declared_weight'] = np.random.uniform(0.5, 30.0, size=num_records).round(2)
# الوزن المحاسب عليه (Billed weight) هو الأكبر بين الفعلي والحجمي
new_data['billed_weight'] = new_data[['declared_weight', 'volumetric_weight_kg']].max(axis=1)


# هـ. تفصيل تكلفة الشحن (Shipping Cost Breakdown)
# السعر الأساسي بناء على المسافة والوزن المحاسب
new_data['base_shipping_cost'] = 20 + (new_data['distance_km'] * 0.03) + (new_data['billed_weight'] * 1.5)
new_data['base_shipping_cost'] = new_data['base_shipping_cost'].round(2)

# رسوم الدفع عند الاستلام (COD Fees) (لنفترض 30% من الطلبات)
new_data['cod_fees'] = np.where(np.random.rand(num_records) < 0.3, 15.0, 0.0)

# الضرائب (Taxes 15%)
new_data['taxes'] = ((new_data['base_shipping_cost'] + new_data['cod_fees']) * 0.15).round(2)

# إجمالي تكلفة الشحن
new_data['total_shipping_cost'] = new_data['base_shipping_cost'] + new_data['cod_fees'] + new_data['taxes']


# و. إضافة مستوى جغرافي أدق (الحي - District)
riyadh_districts = ['Al Olaya', 'Al Sulimaniyah', 'Al Malaz', 'Al Yasmin', 'KAFD', 'Al Murabba']
jeddah_districts = ['Al Safa', 'Al Hamra', 'Al Basateen', 'Obhur', 'Al Balad']
dammam_districts = ['Al Faisaliyah', 'Al Shate', 'Al Nuzha', 'Al Jalawiyah']

def assign_district(city):
    city_str = str(city).lower()
    if 'riyadh' in city_str: return np.random.choice(riyadh_districts)
    if 'jeddah' in city_str: return np.random.choice(jeddah_districts)
    if 'dammam' in city_str: return np.random.choice(dammam_districts)
    return 'District ' + str(np.random.randint(1, 10))

# افترض أن عمودي origin و destination يعبران عن اسم المدينة أو يحتويان عليها
new_data['origin_district'] = new_data['origin'].apply(assign_district)
new_data['destination_district'] = new_data['destination'].apply(assign_district)


# 4. تنظيف وترتيب الأعمدة النهائية
final_columns = [
    'shipment_id', 'tracking_number', 'source_type', 'source_platform', 'source_provider', 'carrier', 
    'origin', 'origin_district', 'destination', 'destination_district',
    'date', 'promised_delivery_date', 'ready_for_pickup_at', 'picked_up_at', 
    'shipped_at', 'out_for_delivery_at', 'delivered_at', 
    'shipment_status', 'lead_time_days', 'delay_hours',
    'length_cm', 'width_cm', 'height_cm', 'volumetric_weight_kg', 
    'declared_weight', 'billed_weight', 
    'distance_km', 'base_shipping_cost', 'cod_fees', 'taxes', 'total_shipping_cost'
]

sample_10k = new_data[final_columns]

# 5. حفظ العينة في ملف CSV
sample_10k.to_csv('saudi_ecommerce_sample_10k.csv', index=False)

print("تم توليد العينة بنجاح: saudi_ecommerce_sample_10k.csv")