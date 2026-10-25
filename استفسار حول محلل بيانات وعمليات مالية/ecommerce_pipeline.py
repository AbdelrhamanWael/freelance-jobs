"""
نظام أتمتة العمليات والتسويات المالية لمتاجر التجارة الإلكترونية
E-Commerce Operations & Financial Reconciliation Pipeline

المسار المعتمد:
Raw OMS Export -> Master Database (Single Source of Truth) -> Smart Filtered Manifests -> Reconciliation & COD Audit
"""

import sys
import os
import openpyxl
import openpyxl.styles.fonts
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import numpy as np
from datetime import datetime

# تجاوز حد خطوط openpyxl للملفات المصدرة من أنظمة طرف ثالث
openpyxl.styles.fonts.Font.family.max = 100

class ECommercePipeline:
    def __init__(self, master_path="Master_Database.xlsx"):
        self.master_path = master_path
        self.master_df = None

    def clean_phone(self, phone):
        """تنظيف وتوحيد أرقام الهواتف واستخراج رمز النداء"""
        if pd.isna(phone):
            return "", 963
        phone_str = str(phone).replace(".0", "").strip()
        # إزالة الرموز
        phone_str = "".join([c for c in phone_str if c.isdigit()])
        
        # كود النداء الافتراضي
        call_code = 963
        if phone_str.startswith("963"):
            call_code = 963
        elif phone_str.startswith("00963"):
            phone_str = phone_str[2:]
            call_code = 963
        return phone_str, call_code

    def standardize_governorate(self, city):
        """
        توحيد وتطبيع أسماء المحافظات السورية الـ 14 بدقة
        يعالج كافة الأخطاء الإملائية وأسماء الأحياء والبلدات المكتوبة خطأً كمدن
        """
        if pd.isna(city):
            return "غير محدد"
        s = str(city).strip()
        
        # ريف دمشق أولاً قبل دمشق لمنع التداخل
        if any(k in s for k in ["ريف دمشق", "قطنا", "دوما", "حرستا", "جرمانا", "صحنايا", "قدسيا", "الكسوة", "داريا", "التل", "عقربا"]):
            return "ريف دمشق"
        # دمشق العاصمة
        if any(k in s for k in ["دمشق", "المزة", "مزه", "المهاجرين", "عدوى", "البرامكة", "كفرسوسة", "شعلان", "مهاجرين", "باب توما", "تجارة", "الميدان"]):
            return "دمشق"
        # حلب وريفها
        if any(k in s for k in ["حلب", "منبج", "عفرين", "اعزاز", "الباب", "الأتارب", "حمدانيه"]):
            return "حلب"
        # إدلب
        if any(k in s for k in ["إدلب", "ادلب", "أدلب", "سراقب", "معرت", "اريحا", "أريحا", "سلقين", "حارم"]):
            return "إدلب"
        # اللاذقية
        if any(k in s for k in ["اللاذقية", "لاذقية", "جبلة", "جبله", "القرداحة", "الحفة"]):
            return "اللاذقية"
        # طرطوس
        if any(k in s for k in ["طرطوس", "بانياس", "صافيتا", "دريكيش", "الشيخ بدر"]):
            return "طرطوس"
        # حمص
        if any(k in s for k in ["حمص", "تدمر", "الرستن", "القصير", "تلكلخ", "السخنة"]):
            return "حمص"
        # حماة
        if any(k in s for k in ["حماة", "حماه", "hamat", "سلمية", "مصياف", "محردة", "السقيلبية"]):
            return "حماة"
        # درعا
        if any(k in s for k in ["درعا", "إزرع", "ازرع", "الصنمين", "الحراك", "نوى", "طفس", "المنشيه"]):
            return "درعا"
        # السويداء
        if any(k in s for k in ["السويداء", "سويداء", "شهبا", "صلخد"]):
            return "السويداء"
        # القنيطرة
        if any(k in s for k in ["القنيطرة", "قنيطرة", "خان أرنبة", "فيق"]):
            return "القنيطرة"
        # دير الزور
        if any(k in s for k in ["دير الزور", "ديرالزور", "الميادين", "البوكمال", "بدير الزور", "الطيانه"]):
            return "دير الزور"
        # الرقة
        if any(k in s for k in ["الرقة", "الرقه", "الطبقة", "تل أبيض", "المنصوره"]):
            return "الرقة"
        # الحسكة
        if any(k in s for k in ["الحسكة", "الحسكه", "حسكة", "القامشلي", "قامشلي", "عامودا", "رأس العين", "كلاسة"]):
            return "الحسكة"
        
        return s

    def load_or_init_master(self, raw_oms_path=None):
        """تحميل الملف المركزي أو إنشاؤه من تصدير الـ OMS المرجعي الأول"""
        if os.path.exists(self.master_path):
            print(f"[+] تحميل الملف المركزي الحالي: {self.master_path}")
            self.master_df = pd.read_excel(self.master_path)
        elif raw_oms_path and os.path.exists(raw_oms_path):
            print(f"[+] إنشاء الملف المركزي التأسيسي من تصدير OMS: {raw_oms_path}")
            df = pd.read_excel(raw_oms_path)
            # إضافة أعمدة تشغيلية وتحليلية
            df["تاريخ الإنشاء الفعلي"] = pd.to_datetime(df["تاريخ الإنشاء"], errors="coerce")
            df["المحافظة_الموحدة"] = df["المدينة"].apply(self.standardize_governorate)
            df["تاريخ_الإضافة_للمركزي"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.master_df = df
            self.save_master()
        else:
            raise FileNotFoundError("لم يتم العثور على الملف المركزي أو تصدير الـ OMS التأسيسي.")
        
        return self.master_df

    def save_master(self):
        """حفظ وتنسيق الملف المركزي مع إزالة المناطق الزمنية لتوافق Excel"""
        if self.master_df is not None:
            # تحويل أي عمود تاريخ يحتوي على منطقة زمنية إلى timezone-unaware
            for col in self.master_df.columns:
                if pd.api.types.is_datetime64_any_dtype(self.master_df[col]):
                    try:
                        if self.master_df[col].dt.tz is not None:
                            self.master_df[col] = self.master_df[col].dt.tz_localize(None)
                    except Exception:
                        pass
            self.master_df.to_excel(self.master_path, index=False)
            print(f"[✓] تم حفظ الملف المركزي بنجاح ({len(self.master_df)} طلباً).")

    def ingest_daily_oms(self, new_oms_path):
        """
        تغذية الملف المركزي بالطلبات الجديدة وتحديث الحالات للطلبات السابقة
        Upsert: Insert new orders, Update status for existing orders
        """
        print(f"\n[1] بدء سحب وتحديث البيانات من تصدير OMS: {new_oms_path}")
        if self.master_df is None:
            self.load_or_init_master()

        new_df = pd.read_excel(new_oms_path)
        new_df["تاريخ الإنشاء الفعلي"] = pd.to_datetime(new_df["تاريخ الإنشاء"], errors="coerce")
        new_df["المحافظة_الموحدة"] = new_df["المدينة"].apply(self.standardize_governorate)
        
        # إنشاء مفتاح المطابقة برقم الطلب
        existing_ids = set(self.master_df["رقم الطلب"].astype(str).str.strip())
        
        updated_count = 0
        new_records = []

        for _, row in new_df.iterrows():
            order_id = str(row["رقم الطلب"]).strip()
            if order_id in existing_ids:
                # تحديث الحالة إذا تغيرت
                idx = self.master_df[self.master_df["رقم الطلب"].astype(str).str.strip() == order_id].index[0]
                old_status = self.master_df.at[idx, "الحالة"]
                new_status = row["الحالة"]
                if old_status != new_status:
                    self.master_df.at[idx, "الحالة"] = new_status
                    self.master_df.at[idx, "تاريخ_آخر_تحديث"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    updated_count += 1
            else:
                row_dict = row.to_dict()
                row_dict["تاريخ_الإضافة_للمركزي"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_records.append(row_dict)

        if new_records:
            add_df = pd.DataFrame(new_records)
            self.master_df = pd.concat([self.master_df, add_df], ignore_index=True)

        self.save_master()
        print(f"[✓] تم بنجاح: إضافة {len(new_records)} طلباً جديداً، وتحديث حالة {updated_count} طلباً.")

    def generate_daily_manifest(self, 
                                target_date=None, 
                                allowed_statuses=("ready_to_ship", "processing"),
                                governorates=None,
                                courier_name=None,
                                courier_routing=None,
                                output_filename="شيت_الشحن_المجهز_اليومي.xlsx",
                                split_by_courier=False):
        """
        توليد شيتات الشحن اليومية للمناديب وشركات التوصيل:
        - فلترة صارمة: فقط الطلبات المؤكدة والجاهزة للشحن.
        - فلترة مخصصة حسب المحافظات (governorates).
        - فلترة مخصصة حسب شركات الشحن (courier_name أو courier_routing).
        - منع تسريب الطلبات الملغاة أو غير المؤكدة.
        - تحويل الأعمدة إلى التمبليت المعتمد لشركات الشحن.
        """
        print(f"\n[2] بدء توليد شيت الشحن اليومي...")
        if self.master_df is None:
            self.load_or_init_master()

        df = self.master_df.copy()

        # 1. فلتر الأمان الأول: الحالات المؤكدة فقط
        filtered = df[df["الحالة"].isin(allowed_statuses)].copy()
        print(f"    - الطلبات الجاهزة للشحن المؤكدة إجمالاً: {len(filtered)} طلب.")

        # 2. فلتر التاريخ (إذا تم تحديده)
        if target_date:
            target_dt = pd.to_datetime(target_date).date()
            date_col = "تاريخ الإنشاء" if "تاريخ الإنشاء" in filtered.columns else "تاريخ الإنشاء الفعلي"
            dt_series = pd.to_datetime(filtered[date_col], errors="coerce")
            filtered = filtered[dt_series.dt.date == target_dt]
            print(f"    - الطلبات المطابقة لتاريخ {target_date}: {len(filtered)} طلب.")

        # 3. فلترة حسب المحافظات المحددة (Governorates Filter)
        if governorates:
            if isinstance(governorates, str):
                governorates = [governorates]
            # تطبيع المحافظات المطلوبة
            gov_clean_list = [self.standardize_governorate(g) for g in governorates]
            filtered["gov_eval"] = filtered["المدينة"].apply(self.standardize_governorate)
            filtered = filtered[filtered["gov_eval"].isin(gov_clean_list)]
            print(f"    - الطلبات بعد فلترة المحافظات {gov_clean_list}: {len(filtered)} طلب.")

        # 4. فلترة حسب شركة الشحن المحددة (Courier Company Filter)
        if courier_name:
            # إذا كانت شركة الشحن مسجلة في الـ OMS
            if "شركة الشحن" in filtered.columns and filtered["شركة الشحن"].dropna().isin([courier_name]).any():
                filtered = filtered[filtered["شركة الشحن"] == courier_name]
                print(f"    - الطلبات المطابقة لشركة الشحن ({courier_name}) من الـ OMS: {len(filtered)} طلب.")
            elif courier_routing and courier_name in courier_routing:
                # إذا كانت معتمدة على قواعد التغطية الجغرافية للشركة
                covered_govs = [self.standardize_governorate(g) for g in courier_routing[courier_name]]
                filtered["gov_eval"] = filtered["المدينة"].apply(self.standardize_governorate)
                filtered = filtered[filtered["gov_eval"].isin(covered_govs)]
                print(f"    - الطلبات الموجهة لشركة ({courier_name}) وفق نطاق تغطيتها {covered_govs}: {len(filtered)} طلب.")

        if len(filtered) == 0:
            print("[!] لا توجد طلبات مؤكدة مطابقة للشروط لتصدير شيت اليوم.")
            return None

        # 5. بناء هيكل الشيت المعتمد لشركات التوصيل (Manifest Template)
        manifest_data = []
        for _, row in filtered.iterrows():
            phone, call_code = self.clean_phone(row.get("الهاتف", ""))
            gov = self.standardize_governorate(row.get("المدينة", ""))
            
            # المنطقة والعنوان
            area = str(row.get("المنطقة", "")).strip() if pd.notna(row.get("المنطقة")) else gov
            address = str(row.get("العنوان", "")).strip() if pd.notna(row.get("العنوان")) else area
            
            # المبلغ (مبلغ التحصيل COD أو الإجمالي)
            amount = row.get("مبلغ COD")
            if pd.isna(amount) or amount == 0:
                amount = row.get("الإجمالي", 0)

            # الكمية والوزن
            qty = row.get("إجمالي الكمية", 1)
            weight = row.get("وزن المنتج (كغ)", 1)
            if pd.isna(weight) or weight == 0:
                weight = 1

            item = {
                "رقم المرجعية": str(row.get("رقم الطلب", "")).strip(),
                "اسم المستلم": str(row.get("المستلم", "")).strip() if pd.notna(row.get("المستلم")) else "عميل",
                "رقم الهاتف": phone,
                "رمز النداء": call_code,
                "المحافظة": gov,
                "المدينة": area,
                "العنوان": address,
                "محتوى الشحنة": str(row.get("اسم المنتج", "")).strip(),
                "المبلغ": float(amount) if pd.notna(amount) else 0.0,
                "العملة": str(row.get("العملة", "USD")).strip(),
                "عدد الطرود": int(qty) if pd.notna(qty) else 1,
                "الوزن": float(weight)
            }
            manifest_data.append(item)

        manifest_df = pd.DataFrame(manifest_data)

        # 6. التصدير بتنسيق Excel احترافي
        self._export_styled_excel(manifest_df, output_filename, title="بيان شحنات التوصيل اليومي")
        print(f"[✓] تم توليد شيت الشحن بنجاح: {output_filename} ({len(manifest_df)} شحنة).")

        # 7. التوزيع الذكي حسب المناطق (Routing by Region)
        if split_by_courier:
            self._split_by_courier_and_region(manifest_df, courier_routing)

        return manifest_df

    def _split_by_courier_and_region(self, manifest_df, courier_routing=None):
        """
        تقسيم الشحنات تلقائياً إلى ملفات فرعية:
        - إما حسب شركات الشحن المعتمدة (Babel Express, شركة دمشق، إلخ).
        - أو حسب التوزيع الجغرافي للمحافظات.
        """
        print("\n[3] بدء التوزيع الآلي حسب شركات الشحن / المحافظات:")
        
        # إذا تم تمرير مصفوفة توزيع شركات الشحن
        if courier_routing:
            for courier, govs in courier_routing.items():
                clean_govs = [self.standardize_governorate(g) for g in govs]
                sub_df = manifest_df[manifest_df["المحافظة"].isin(clean_govs)]
                if len(sub_df) > 0:
                    safe_name = f"شيت_شركة_{courier.replace(' ', '_')}.xlsx"
                    self._export_styled_excel(sub_df, safe_name, title=f"شحنات شركة {courier}")
                    print(f"    - {safe_name} ({courier}): {len(sub_df)} شحنة مغطية للمحافظات: {clean_govs}")
        else:
            # التوزيع الجغرافي الافتراضي لشركات التوصيل
            regions = {
                "شيت_شركة_الشام_دمشق_وريفها.xlsx": ["دمشق", "ريف دمشق"],
                "شيت_شركة_الشمال_حلب_وإدلب.xlsx": ["حلب", "إدلب"],
                "شيت_شركة_الوسط_والساحل.xlsx": ["حمص", "حماة", "اللاذقية", "طرطوس"],
                "شيت_شركة_المناطق_الشرقية_والجنوبية.xlsx": ["درعا", "السويداء", "القنيطرة", "دير الزور", "الرقة", "الحسكة"]
            }
            for filename, govs in regions.items():
                clean_govs = [self.standardize_governorate(g) for g in govs]
                sub_df = manifest_df[manifest_df["المحافظة"].isin(clean_govs)]
                if len(sub_df) > 0:
                    self._export_styled_excel(sub_df, filename, title=f"منافست تسليم - {filename.replace('.xlsx', '')}")
                    print(f"    - {filename}: {len(sub_df)} شحنة مجهزة.")

    def _export_styled_excel(self, df, filename, title="Manifest"):
        """تنسيق ملف الإكسيل ليكون جاهزاً للطباعة والتسليم الفوري للمناديب"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "قائمة الشحن"
        ws.views.sheetView[0].rightToLeft = True  # اتجاه من اليمين لليسار

        # ألوان وهوية بصرية
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Calibri", size=10)
        border_thin = Side(border_style="thin", color="D9D9D9")
        cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # كتابة العناوين
        headers = df.columns.tolist()
        ws.append(headers)
        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = cell_border
        ws.row_dimensions[1].height = 28

        # كتابة البيانات
        for row_idx, row_data in enumerate(df.values, start=2):
            ws.append(list(row_data))
            ws.row_dimensions[row_idx].height = 22
            for col_num in range(1, len(headers) + 1):
                cell = ws.cell(row=row_idx, column=col_num)
                cell.font = data_font
                cell.border = cell_border
                cell.alignment = center_align

        # ضبط عرض الأعمدة تلقائياً
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 40)

        try:
            wb.save(filename)
        except PermissionError:
            alt_filename = filename.replace(".xlsx", f"_محدث_{datetime.now().strftime('%H%M%S')}.xlsx")
            wb.save(alt_filename)
            filename = alt_filename

    def reconcile_dispatches(self, manifest_files, raw_oms_path, report_output="تقرير_المطابقة_والتدقيق_المالي.xlsx"):
        """
        المطابقة والتدقيق المالي (Daily Reconciliation & Audit):
        - مطابقة الشيتات المسلمة مع الـ OMS
        - كشف الطلبات المعلقة التي لم تخرج (مثل الـ 31 طلباً ليوم 12)
        - التحقق من إجمالي مبالغ الـ COD المتوقعة
        - توليد تقرير إكسيل تنفيذي مفصل
        """
        print(f"\n[4] تنفيذ التدقيق والمطابقة التشغيلية والمالية...")
        df_oms = pd.read_excel(raw_oms_path)
        df_oms.columns = [c.strip() for c in df_oms.columns]
        df_oms["order_id_clean"] = df_oms["رقم الطلب"].astype(str).str.strip()
        
        # 1. تجميع طلبات الشيتات اليومية
        manifest_records = []
        for f in manifest_files:
            if os.path.exists(f):
                m_df = pd.read_excel(f)
                m_df.columns = [c.strip() for c in m_df.columns]
                m_df = m_df.dropna(subset=["رقم المرجعية"])
                m_df["المصدر_الشيت"] = f
                manifest_records.append(m_df)

        if not manifest_records:
            print("[!] لم يتم العثور على شيتات مطابقة.")
            return

        all_manifests_df = pd.concat(manifest_records, ignore_index=True)
        all_manifests_df["order_id_clean"] = all_manifests_df["رقم المرجعية"].astype(str).str.strip()
        
        dispatched_ids = set(all_manifests_df["order_id_clean"])
        total_manifest_amount = all_manifests_df["المبلغ"].sum() if "المبلغ" in all_manifests_df.columns else 0.0

        print(f"    - إجمالي الطلبات المخرجة في شيتات الشحن: {len(dispatched_ids)} طلب فريد.")
        print(f"    - إجمالي مبالغ الـ COD المطلوبة للتحصيل: {total_manifest_amount:,.2f} $")

        # 2. فحص طلبات 12-9 في OMS لتحديد المعلق
        df_oms["creation_dt"] = pd.to_datetime(df_oms["تاريخ الإنشاء"], errors="coerce")
        oms_12 = df_oms[df_oms["creation_dt"].dt.date == pd.to_datetime("2026-09-12").date()].copy()
        
        # الطلبات المعلقة في 12-9
        pending_12 = oms_12[~oms_12["order_id_clean"].isin(dispatched_ids)].copy()
        print(f"    - طلبات منشأة في 12-9 ولم تخرج في الشيت (معلقة): {len(pending_12)} طلب.")

        # 3. تتبع الحالات الحالية لشحنات شيت 11-9 في OMS
        sheet_11_ids = set(all_manifests_df[all_manifests_df["المصدر_الشيت"].str.contains("١١|11")]["order_id_clean"])
        oms_11_tracked = df_oms[df_oms["order_id_clean"].isin(sheet_11_ids)].copy()

        # 4. بناء تقرير الإكسيل التنفيذي مع حماية من قفل الملفات المفتوحة
        target_file = report_output
        try:
            writer = pd.ExcelWriter(target_file, engine="openpyxl")
        except PermissionError:
            target_file = report_output.replace(".xlsx", f"_محدث_{datetime.now().strftime('%H%M%S')}.xlsx")
            writer = pd.ExcelWriter(target_file, engine="openpyxl")

        with writer:
            # شيت 1: الملخص التنفيذي
            summary_data = [
                {"المؤشر التشغيلي / المالي": "إجمالي طلبات الشحن المخرجة (11 و 12 سبتمبر)", "القيمة": len(dispatched_ids), "الوحدة": "طلب"},
                {"المؤشر التشغيلي / المالي": "إجمالي مبالغ COD المطلوبة للتحصيل من الشركتين", "القيمة": round(total_manifest_amount, 2), "الوحدة": "دولار USD"},
                {"المؤشر التشغيلي / المالي": "طلبات منشأة في 12-9 وخرجت للشحن", "القيمة": len(oms_12) - len(pending_12), "الوحدة": "طلب"},
                {"المؤشر التشغيلي / المالي": "طلبات 12-9 المعلقة (بانتظار التأكيد)", "القيمة": len(pending_12), "الوحدة": "طلب معلق"},
                {"المؤشر التشغيلي / المالي": "نسبة الإنجاز الفوري لطلبات 12-9", "القيمة": f"{((len(oms_12) - len(pending_12))/len(oms_12)*100):.1f}%", "الوحدة": "معدل تنفيذ"}
            ]
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="الملخص_التنفيذي", index=False)

            # شيت 2: تفاصيل الطلبات المعلقة ليوم 12-9
            pending_cols = ["رقم الطلب", "الحالة", "المستلم", "الهاتف", "المدينة", "اسم المنتج", "مبلغ COD", "الإجمالي", "تاريخ الإنشاء"]
            avail_pending_cols = [c for c in pending_cols if c in pending_12.columns]
            pending_export = pending_12[avail_pending_cols].copy()
            if "تاريخ الإنشاء" in pending_export.columns:
                pending_export["تاريخ الإنشاء"] = pending_export["تاريخ الإنشاء"].astype(str)
            pending_export.to_excel(writer, sheet_name="طلبات_12-9_المعلقة", index=False)

            # شيت 3: تتبع حالات شحنات 11-9
            status_summary = oms_11_tracked["الحالة"].value_counts().reset_index()
            status_summary.columns = ["الحالة الحالية في الـ OMS", "عدد الطلبات"]
            status_summary.to_excel(writer, sheet_name="تتبع_حالات_11-9", index=False)

        print(f"[✓] تم إنشاء تقرير المطابقة والتدقيق التنفيذي: {target_file}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    
    pipeline = ECommercePipeline(master_path="Master_Database.xlsx")
    
    # 1. تهيئة الملف المركزي الشامل من OMS
    pipeline.load_or_init_master(raw_oms_path="oms-orders-2026-09-13.xlsx")

    # 2. مثال أ: مصفوفة توزيع وتغطية شركات الشحن (Courier Routing Rules)
    # كل شركة شحن تستلم المحافظات التي تغطيها رسمياً
    courier_matrix = {
        "بابل إكسبريس (Babel Express)": ["حلب", "إدلب"],
        "أجنحة الشام للتوصيل": ["دمشق", "ريف دمشق"],
        "النورس إكسبريس الساحل والوسط": ["حمص", "حماة", "اللاذقية", "طرطوس"],
        "الفرات للشحن السريع": ["دير الزور", "الرقة", "الحسكة", "درعا", "السويداء", "القنيطرة"]
    }

    # 3. مثال ب: توليد شيت شحن اليوم (13/9) مع التوزيع الآلي حسب شركات الشحن
    manifest_13 = pipeline.generate_daily_manifest(
        target_date="2026-09-13",
        allowed_statuses=["ready_to_ship", "processing"],
        output_filename="شيت_شحن_اليوم_13-9-2026_مؤكد_فقط.xlsx",
        courier_routing=courier_matrix,
        split_by_courier=True
    )

    # 4. مثال ج: فلترة مخصصة لمحافظات معينة فقط (مثل حلب ودمشق)
    pipeline.generate_daily_manifest(
        target_date="2026-09-13",
        governorates=["حلب", "دمشق"],
        output_filename="شيت_مخصص_حلب_ودمشق_13-9.xlsx"
    )

    # 5. مطابقة الشيتات السابقة (11 و 12 سبتمبر) وتدقيق الـ COD
    pipeline.reconcile_dispatches(
        manifest_files=["طلبات-١١-٩-٢٠٢٦-نهائي.xlsx", "طلبات-12-9-2026.xlsx"],
        raw_oms_path="oms-orders-2026-09-13.xlsx",
        report_output="تقرير_المطابقة_والتدقيق_المالي.xlsx"
    )
