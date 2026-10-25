# -*- coding: utf-8 -*-
"""
توليد ملفات الإكسل مع تحديث أرقام الواتساب لتكون:
1. مسبوقة بعلامة + (مثال: +966530046521) حتى يتعرف عليها تطبيق واتساب فوراً كرابط أخضر قابل للنقر عند نسخها.
2. مفعّلة كرابط تشعبي (Hyperlink) في الإكسل، بحيث يؤدي الضغط عليها مباشرة داخل الإكسل لفتح محادثة واتساب (wa.me).
3. إضافة عمود مخصص لرابط محادثة واتساب المباشر (wa.me) لسهولة الاستخدام.
"""

import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# قائمة الـ 30 معلماً المستقلين: يوتيوب أولاً ثم إكس
TEACHERS = [
    # ==================== 1. معلمي يوتيوب (الأولوية الأولى) ====================
    {
        "name": "أ. محمد الرفاعي",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=0_cNwppYaNE",
        "specialty": "كمي",
        "phone": "966530046521",
        "notes": "قناة لشرح قدرات كمي وتأسيس"
    },
    {
        "name": "د. كريم (qudratDr karim)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=eBqdo9NhpaI",
        "specialty": "قدرات (عام)",
        "phone": "966549172952",
        "notes": "شروحات قدرات وتجميعات محوسب"
    },
    {
        "name": "أ. إيهاب فهمي (GAT4U)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=0gnBcmzFa20",
        "specialty": "قدرات (عام)",
        "phone": "966569061170",
        "notes": "شرح تجميعات ونماذج القدرات"
    },
    {
        "name": "مستر علاء رسلان (MR. RASLAN)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=2EMd8HZNx1w",
        "specialty": "قدرات (عام)",
        "phone": "966565016982",
        "notes": "دروس قدرات وتحصيلي تأسيس وتدريب"
    },
    {
        "name": "أ. سالم زهرة",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=KeQmUo8bIlI",
        "specialty": "كمي",
        "phone": "966542372928",
        "notes": "شرح مسائل القدرات الكمي ونماذج الـ 120"
    },
    {
        "name": "المدرب تامر الصاوي (tamerGAT)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=Sd38n76uB1Q",
        "specialty": "قدرات (عام)",
        "phone": "966553676132",
        "notes": "مدرب قدرات وتجميعات حديثة"
    },
    {
        "name": "أ. فهيد الشمري",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=fmyziblnqYU",
        "specialty": "قدرات (عام)",
        "phone": "966509950956",
        "notes": "معلم قدرات وشروحات تدريبية"
    },
    {
        "name": "د. محمد الشاعر",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=fxK1gPnN7_Y",
        "specialty": "كمي",
        "phone": "966567338081",
        "notes": "شرح أساسيات القدرات والتحصيلي"
    },
    {
        "name": "أ. إيمان وهدان (Eman Wahdan)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=RkhC0FQvBC0",
        "specialty": "قدرات (عام)",
        "phone": "966501138137",
        "notes": "معلمة قدرات خصوصي وشروحات"
    },
    {
        "name": "أ. روان (قدرات روان)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=cLhvIExbh4o",
        "specialty": "قدرات (عام)",
        "phone": "966535266025",
        "notes": "شروحات مبسطة لاختبار القدرات"
    },
    {
        "name": "أبو عمران (قدرات كمي)",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=E0sp13Pt_i4",
        "specialty": "كمي",
        "phone": "966536581290",
        "notes": "معلم قدرات كمي وحل تجميعات"
    },
    {
        "name": "أ. جمال عبدالله",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=bluQuKnnPSA",
        "specialty": "كمي",
        "phone": "966532860447",
        "notes": "معلم رياضيات وقدرات كمي"
    },
    {
        "name": "أ. عبدالمنعم جوهر",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=q6qW7uGgTfs",
        "specialty": "لفظي",
        "phone": "966549257154",
        "notes": "معلم قدرات لفظي وتناظر لفظي"
    },
    {
        "name": "أ. شعبان حمادة",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=gT8o6-e_bN4",
        "specialty": "لفظي",
        "phone": "966508121578",
        "notes": "شروحات قدرات لفظي واستيعاب المقروء"
    },
    {
        "name": "أ. رغد الفرشان",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=uK1Xm_q319Y",
        "specialty": "قدرات (عام)",
        "phone": "966501490718",
        "notes": "معلمة قدرات وتدريب خصوصي"
    },
    {
        "name": "مدرس قدرات ورياضيات جامعي",
        "platform": "YouTube",
        "url": "https://www.youtube.com/watch?v=YKN-PRgOEpM",
        "specialty": "كمي",
        "phone": "966559704045",
        "notes": "تدريس قدرات كمي ورياضيات بالرياض"
    },

    # ==================== 2. معلمي منصة إكس (Twitter) ====================
    {
        "name": "أ. أشرف سليمان (معلم قدرات كمي)",
        "platform": "X (Twitter)",
        "url": "https://x.com/AshrfShsah",
        "specialty": "كمي",
        "phone": "966532687910",
        "notes": "معلم قدرات كمي متخصص بالرياض"
    },
    {
        "name": "أ. منى (معلمة قدرات وتحصيلي)",
        "platform": "X (Twitter)",
        "url": "https://x.com/NnS8wqFtdSTDidn",
        "specialty": "كمي",
        "phone": "966560957545",
        "notes": "معلمة قدرات وتحصيلي ورياضيات"
    },
    {
        "name": "أ. أمل (معلمة قدرات وتحصيلي)",
        "platform": "X (Twitter)",
        "url": "https://x.com/amal8294415860",
        "specialty": "كمي + لفظي",
        "phone": "966581441101",
        "notes": "معلمة قدرات وتحصيلي تأسيس وتدريب"
    },
    {
        "name": "أ. فهيد سلمان",
        "platform": "X (Twitter)",
        "url": "https://x.com/fahaidslman",
        "specialty": "قدرات (عام)",
        "phone": "966509950956",
        "notes": "معلم ومدرب قدرات"
    },
    {
        "name": "أ. تركي السهلي",
        "platform": "X (Twitter)",
        "url": "https://x.com/Turki_alsahle1",
        "specialty": "قدرات (عام)",
        "phone": "966549599449",
        "notes": "معلم خصوصي قدرات وتدريب"
    },
    {
        "name": "د. سحر أحمد (Dr. Sahar Ahmed)",
        "platform": "X (Twitter)",
        "url": "https://x.com/SaharA73321",
        "specialty": "كمي + لفظي",
        "phone": "966599064204",
        "notes": "تدريس قدرات وتحصيلي خصوصي"
    },
    {
        "name": "أ. عمر (أستاذ اللفظي)",
        "platform": "X (Twitter)",
        "url": "https://x.com/mr3514585972119",
        "specialty": "لفظي",
        "phone": "966557347832",
        "notes": "معلم متخصص في القسم اللفظي"
    },
    {
        "name": "أ. إبراهيم (مدرس قدرات)",
        "platform": "X (Twitter)",
        "url": "https://x.com/e_nawb1",
        "specialty": "قدرات (عام)",
        "phone": "966556508342",
        "notes": "مدرس قدرات كمي ولفظي"
    },
    {
        "name": "أ. بدر (مدقق لغوي ومعلم لفظي)",
        "platform": "X (Twitter)",
        "url": "https://x.com/ooGYpVPixJsPHQB",
        "specialty": "لفظي",
        "phone": "966557067269",
        "notes": "معلم قدرات لفظي وتأسيس استيعاب"
    },
    {
        "name": "م. كامل (معلم قدرات كمي وإحصاء)",
        "platform": "X (Twitter)",
        "url": "https://x.com/kamelabusamra",
        "specialty": "كمي",
        "phone": "966530605399",
        "notes": "تدريس قدرات كمي وتحليل مسائل"
    },
    {
        "name": "د. ماث (Dr Math - قدرات كمي)",
        "platform": "X (Twitter)",
        "url": "https://x.com/Dr_Math4u",
        "specialty": "كمي",
        "phone": "966565046450",
        "notes": "معلم قدرات كمي وحساب ذهني"
    },
    {
        "name": "أ. رنا (Rana - قدرات)",
        "platform": "X (Twitter)",
        "url": "https://x.com/jnhlfrd80658831",
        "specialty": "قدرات (عام)",
        "phone": "966545385974",
        "notes": "معلمة قدرات وتدريب خصوصي"
    },
    {
        "name": "أ. ساره (تدريب قدرات ورخصة)",
        "platform": "X (Twitter)",
        "url": "https://x.com/Sarah_21al",
        "specialty": "كمي",
        "phone": "966581019236",
        "notes": "معلمة قدرات وشروحات كمي"
    },
    {
        "name": "مدرس قدرات وتحصيلي بالرياض",
        "platform": "X (Twitter)",
        "url": "https://x.com/qdratqiyas4u",
        "specialty": "قدرات (عام)",
        "phone": "966548434100",
        "notes": "مدرس قدرات خصوصي حضوري وأونلاين"
    }
]

def format_teacher_rows(teachers_list):
    """
    تحضير الصفوف مع تنسيق رقم الواتساب:
    - يبدأ بـ + (مثل: +966530046521)
    - إضافة رابط محادثة واتساب المباشر wa.me
    """
    rows = []
    for i, t in enumerate(teachers_list, start=1):
        clean_phone = t["phone"].lstrip("+")
        formatted_phone = f"+{clean_phone}"
        wa_link = f"https://wa.me/{clean_phone}"
        rows.append([
            i,
            t["name"],
            t["platform"],
            t["specialty"],
            formatted_phone,
            wa_link,
            t["url"],
            t["notes"]
        ])
    return rows

def style_worksheet(ws, headers, rows_count):
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    body_font = Font(name="Segoe UI", size=10)
    link_font = Font(name="Segoe UI", size=10, color="1D4ED8", underline="single")
    phone_font = Font(name="Segoe UI", size=10, bold=True, color="059669", underline="single") # Emerald WhatsApp color
    youtube_fill = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
    x_fill = PatternFill(start_color="F0F9FF", end_color="F0F9FF", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )

    ws.row_dimensions[1].height = 30
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    for r_idx in range(2, rows_count + 2):
        ws.row_dimensions[r_idx].height = 26
        platform_cell = ws.cell(row=r_idx, column=3).value or ""
        row_fill = youtube_fill if "YouTube" in platform_cell else x_fill
        
        for c_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=r_idx, column=c_idx)
            cell.font = body_font
            cell.border = thin_border
            cell.fill = row_fill
            
            # Alignments
            # 1: م, 3: المنصة, 4: التخصص, 5: رقم الواتساب, 6: رابط واتساب مباشر
            if c_idx in [1, 3, 4, 5, 6]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                
            # 5: رقم الواتساب (+9665...) -> مفعّل برابط wa.me
            if c_idx == 5:
                phone_val = str(cell.value or "")
                clean_num = phone_val.lstrip("+")
                cell.number_format = "@"
                cell.value = phone_val
                cell.hyperlink = f"https://wa.me/{clean_num}"
                cell.font = phone_font
                
            # 6: رابط واتساب مباشر
            if c_idx == 6:
                url = str(cell.value or "")
                cell.hyperlink = url
                cell.font = link_font
                
            # 7: رابط القناة / الحساب
            if c_idx == 7:
                url = str(cell.value or "")
                cell.hyperlink = url
                cell.font = link_font

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

def build_files():
    import csv

    headers = [
        "م", 
        "اسم المعلم", 
        "المنصة", 
        "التخصص", 
        "رقم الواتساب (+)", 
        "رابط محادثة واتساب المباشر", 
        "رابط القناة / الحساب", 
        "ملاحظات وتفاصيل"
    ]

    # 1. ملف الـ 30 معلماً الكامل
    wb30 = openpyxl.Workbook()
    ws30 = wb30.active
    ws30.title = "معلمي القدرات الأفراد"
    ws30.views.sheetView[0].rightToLeft = True
    ws30.append(headers)
    rows30 = format_teacher_rows(TEACHERS)
    for r in rows30:
        ws30.append(r)
    style_worksheet(ws30, headers, len(rows30))
    wb30.save("qudrat_individual_teachers_30.xlsx")
    print("[✓] تم حفظ: qudrat_individual_teachers_30.xlsx")

    with open("qudrat_individual_teachers_30.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows30)
    print("[✓] تم حفظ: qudrat_individual_teachers_30.csv")

    # 2. ملف العينة (5 معلمين: يوتيوب + إكس)
    sample_5_teachers = [
        TEACHERS[0],  # أ. محمد الرفاعي (YouTube - كمي)
        TEACHERS[12], # أ. عبدالمنعم جوهر (YouTube - لفظي)
        TEACHERS[7],  # د. محمد الشاعر (YouTube - عام)
        TEACHERS[16], # أ. أشرف سليمان (X - كمي)
        TEACHERS[18], # أ. أمل (X - كمي + لفظي)
    ]
    wb5 = openpyxl.Workbook()
    ws5 = wb5.active
    ws5.title = "عينة معلمين (يوتيوب وإكس)"
    ws5.views.sheetView[0].rightToLeft = True
    ws5.append(headers)
    rows5 = format_teacher_rows(sample_5_teachers)
    for r in rows5:
        ws5.append(r)
    style_worksheet(ws5, headers, len(rows5))
    wb5.save("qudrat_sample_5_teachers.xlsx")
    print("[✓] تم حفظ: qudrat_sample_5_teachers.xlsx")

    with open("qudrat_sample_5_teachers.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows5)
    print("[✓] تم حفظ: qudrat_sample_5_teachers.csv")

if __name__ == "__main__":
    build_files()
