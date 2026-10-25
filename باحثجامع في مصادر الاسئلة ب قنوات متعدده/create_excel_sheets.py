import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def create_monitoring_sheet():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "الرصد المباشر"
    
    # Enable Right-to-Left layout
    ws.sheet_view.rightToLeft = True
    
    # Fonts
    title_font = Font(name="Segoe UI", size=15, bold=True, color="1E3A8A")
    note_font = Font(name="Segoe UI", size=10, italic=True, color="475569")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    cell_font = Font(name="Segoe UI", size=10, color="0F172A")
    placeholder_font = Font(name="Segoe UI", size=10, italic=True, color="94A3B8")
    
    # Fills & Colors
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Deep Indigo/Navy
    high_priority_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Light Red
    high_priority_font = Font(name="Segoe UI", size=10, bold=True, color="991B1B")
    
    normal_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid") # Slate light
    normal_font = Font(name="Segoe UI", size=10, color="334155")
    
    thin_border = Border(
        left=Side(style='thin', color="CBD5E1"),
        right=Side(style='thin', color="CBD5E1"),
        top=Side(style='thin', color="CBD5E1"),
        bottom=Side(style='thin', color="CBD5E1")
    )
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    # Title & Instruction Banner
    ws.merge_cells("A1:C1")
    ws["A1"] = "📊 ملف الرصد المباشر لتوثيق الرسائل الجاهزة"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[1].height = 30
    
    ws.merge_cells("A2:C2")
    ws["A2"] = "📌 ملاحظة: يُستخدم لتوثيق الرسائل الجاهزة. احرص دائماً على تعبئة صفوف 'أولوية عالية' في أعلى الملف كما طلب العميل."
    ws["A2"].font = note_font
    ws["A2"].alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[2].height = 24
    
    # Headers in Row 4
    headers = ["التصنيف", "سكرين شوت", "رابط الرسالة"]
    ws.row_dimensions[4].height = 30
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
    
    # Sample rows from prompt
    sample_rows = [
        ("أولوية عالية", "[📷 صورة / 📎 ملف PDF]", "[ضع الرابط هنا]"),
        ("أولوية عالية", "[📷 صورة / 📎 ملف PDF]", "[ضع الرابط هنا]"),
        ("حديث غير محدد", "[📷 صورة / 📎 ملف PDF]", "[ضع الرابط هنا]"),
        ("حديث غير محدد", "[📷 صورة / 📎 ملف PDF]", "[ضع الرابط هنا]"),
    ]
    
    start_row = 5
    for idx, (category, screenshot, link) in enumerate(sample_rows):
        r = start_row + idx
        ws.row_dimensions[r].height = 55  # Space for screenshot insertion
        
        # Category
        c1 = ws.cell(row=r, column=1, value=category)
        c1.alignment = align_center
        c1.border = thin_border
        if category == "أولوية عالية":
            c1.fill = high_priority_fill
            c1.font = high_priority_font
        else:
            c1.fill = normal_fill
            c1.font = normal_font
            
        # Screenshot
        c2 = ws.cell(row=r, column=2, value=screenshot)
        c2.alignment = align_center
        c2.border = thin_border
        c2.font = placeholder_font
        
        # Link
        c3 = ws.cell(row=r, column=3, value=link)
        c3.alignment = align_center
        c3.border = thin_border
        c3.font = placeholder_font

    # Add 25 blank formatted rows ready for new entries
    total_rows = start_row + len(sample_rows) + 25
    for r in range(start_row + len(sample_rows), total_rows + 1):
        ws.row_dimensions[r].height = 45
        for col_idx in range(1, 4):
            c = ws.cell(row=r, column=col_idx, value="")
            c.alignment = align_center
            c.border = thin_border
            c.font = cell_font

    # Set column widths
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 45
    
    # Data Validation for 'التصنيف'
    dv = DataValidation(type="list", formula1='"أولوية عالية,حديث غير محدد"', allow_blank=True)
    dv.prompt = "اختر التصنيف من القائمة"
    dv.promptTitle = "التصنيف"
    dv.error = "الرجاء اختيار تصنيف صحيح: (أولوية عالية / حديث غير محدد)"
    dv.errorTitle = "قيمة غير صالحة"
    ws.add_data_validation(dv)
    dv.add(f"A5:A{total_rows}")
    
    # Conditional formatting rules
    ws.conditional_formatting.add(
        f"A5:A{total_rows}",
        CellIsRule(operator='equal', formula=['"أولوية عالية"'], fill=high_priority_fill, font=high_priority_font)
    )
    ws.conditional_formatting.add(
        f"A5:A{total_rows}",
        CellIsRule(operator='equal', formula=['"حديث غير محدد"'], fill=normal_fill, font=normal_font)
    )

    filename = "الإكسل الأول - الرصد المباشر.xlsx"
    wb.save(filename)
    # Also save with alternative simple name for user convenience
    wb.save("الرصد_المباشر.xlsx")
    print(f"Successfully generated: {filename}")


def create_outreach_sheet():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "التواصل وجمع البيانات"
    
    # Enable Right-to-Left layout
    ws.sheet_view.rightToLeft = True
    
    # Fonts
    title_font = Font(name="Segoe UI", size=15, bold=True, color="0F766E")
    note_font = Font(name="Segoe UI", size=10, italic=True, color="475569")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    cell_font = Font(name="Segoe UI", size=10, color="0F172A")
    placeholder_font = Font(name="Segoe UI", size=10, italic=True, color="94A3B8")
    
    # Fills & Colors
    header_fill = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid") # Deep Teal
    replied_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Light Emerald Green
    replied_font = Font(name="Segoe UI", size=10, bold=True, color="166534")
    
    waiting_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Light Amber
    waiting_font = Font(name="Segoe UI", size=10, bold=True, color="92400E")
    
    thin_border = Border(
        left=Side(style='thin', color="CBD5E1"),
        right=Side(style='thin', color="CBD5E1"),
        top=Side(style='thin', color="CBD5E1"),
        bottom=Side(style='thin', color="CBD5E1")
    )
    
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    
    # Title & Subtitle Banner
    ws.merge_cells("A1:D1")
    ws["A1"] = "📋 ملف التواصل وجمع البيانات - متابعة الطلاب اليومية"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[1].height = 30
    
    ws.merge_cells("A2:D2")
    ws["A2"] = "📌 ملاحظة: يُستخدم لتوثيق محاولات التواصل مع الـ 6 طلاب يومياً ومتابعة ردودهم وتحديث الحالة."
    ws["A2"].font = note_font
    ws["A2"].alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[2].height = 24
    
    # Headers in Row 4
    headers = [
        "حالة التواصل (تم الرد / في الانتظار)",
        "رابط حساب الطالب أو رسالته",
        "رد الطالب (الأسئلة والتجربة)",
        "سكرين شوت للمحادثة"
    ]
    ws.row_dimensions[4].height = 30
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = thin_border
    
    # Sample rows from prompt
    sample_rows = [
        ("تم الرد", "[الرابط]", "[نص الرد]", "[📷 صورة / 📎 ملف PDF]"),
        ("في الانتظار", "[الرابط]", "[يُترك فارغاً لحين الرد]", "[يُترك فارغاً]")
    ]
    
    start_row = 5
    for idx, (status, link, response, screenshot) in enumerate(sample_rows):
        r = start_row + idx
        ws.row_dimensions[r].height = 55  # Space for conversation screenshot & multi-line answer
        
        # Col 1: Status
        c1 = ws.cell(row=r, column=1, value=status)
        c1.alignment = align_center
        c1.border = thin_border
        if status == "تم الرد":
            c1.fill = replied_fill
            c1.font = replied_font
        else:
            c1.fill = waiting_fill
            c1.font = waiting_font
            
        # Col 2: Profile/Message Link
        c2 = ws.cell(row=r, column=2, value=link)
        c2.alignment = align_center
        c2.border = thin_border
        c2.font = placeholder_font
        
        # Col 3: Student response
        c3 = ws.cell(row=r, column=3, value=response)
        c3.alignment = align_center if "[" in response else align_right
        c3.border = thin_border
        c3.font = placeholder_font
        
        # Col 4: Conversation Screenshot
        c4 = ws.cell(row=r, column=4, value=screenshot)
        c4.alignment = align_center
        c4.border = thin_border
        c4.font = placeholder_font

    # Pre-format rows for daily work (e.g. 30 rows = 5 days x 6 students)
    total_rows = start_row + len(sample_rows) + 30
    for r in range(start_row + len(sample_rows), total_rows + 1):
        ws.row_dimensions[r].height = 45
        for col_idx in range(1, 5):
            c = ws.cell(row=r, column=col_idx, value="")
            c.alignment = align_right if col_idx == 3 else align_center
            c.border = thin_border
            c.font = cell_font

    # Set column widths
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 38
    ws.column_dimensions["C"].width = 50
    ws.column_dimensions["D"].width = 30
    
    # Data Validation for 'حالة التواصل'
    dv = DataValidation(type="list", formula1='"تم الرد,في الانتظار"', allow_blank=True)
    dv.prompt = "اختر حالة التواصل"
    dv.promptTitle = "حالة التواصل"
    dv.error = "الرجاء الاختيار: (تم الرد / في الانتظار)"
    dv.errorTitle = "قيمة غير صالحة"
    ws.add_data_validation(dv)
    dv.add(f"A5:A{total_rows}")
    
    # Conditional Formatting
    ws.conditional_formatting.add(
        f"A5:A{total_rows}",
        CellIsRule(operator='equal', formula=['"تم الرد"'], fill=replied_fill, font=replied_font)
    )
    ws.conditional_formatting.add(
        f"A5:A{total_rows}",
        CellIsRule(operator='equal', formula=['"في الانتظار"'], fill=waiting_fill, font=waiting_font)
    )

    filename = "الإكسل الثاني - التواصل وجمع البيانات.xlsx"
    wb.save(filename)
    # Also save with alternative simple name
    wb.save("التواصل_وجمع_البيانات.xlsx")
    print(f"Successfully generated: {filename}")

if __name__ == "__main__":
    create_monitoring_sheet()
    create_outreach_sheet()
