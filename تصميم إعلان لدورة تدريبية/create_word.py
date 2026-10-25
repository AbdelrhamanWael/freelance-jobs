import docx
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT

# Create a new Document
doc = docx.Document()

# Set RTL direction for the document (though python-docx might need raw xml for full RTL support, we do our best)
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(12)

# Title
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("معهد مئة وثمانون درجة العالي للتدريب\n")
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(59, 164, 166)
run.bold = True

run = p.add_run("دورة التأسيس لاختبار القدرات\n")
run.font.size = Pt(28)
run.font.color.rgb = RGBColor(217, 111, 99)
run.bold = True

run = p.add_run("(كمي ولفظي)\n")
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(59, 164, 166)
run.bold = True

# Features
doc.add_paragraph("دورة شاملة", style='Heading 2')
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
features = [
    "إتقان الكمي واللفظي من الصفر",
    "أسرار الحل السريع بدون تعقيد",
    "محاكاة واقعية لاختبار قياس",
    "تحليل أداء وتطوير نقاط الضعف",
    "إدارة وقت ذكية تحت الضغط",
    "مهارات تركيز واختيار الإجابة"
]
for f in features:
    run = p.add_run("✔️ " + f + "\n")
    run.font.size = Pt(14)

# Trainers Section
doc.add_paragraph("قسم الطلاب (المدربين)", style='Heading 2')
table = doc.add_table(rows=1, cols=3)
table.alignment = WD_ALIGN_PARAGRAPH.CENTER
row_cells = table.rows[0].cells
row_cells[0].text = "د. فهد الزماي"
row_cells[1].text = "أ. سعد اللويش"
row_cells[2].text = "أ. مشاري العديم"

for cell in row_cells:
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.font.bold = True
            run.font.size = Pt(14)

doc.add_paragraph("قسم الطالبات (المدربات)", style='Heading 2')
table2 = doc.add_table(rows=1, cols=2)
table2.alignment = WD_ALIGN_PARAGRAPH.CENTER
row_cells2 = table2.rows[0].cells
row_cells2[0].text = "أ. موضي الشمري"
row_cells2[1].text = "أ. نوف الشمري"

for cell in row_cells2:
    for paragraph in cell.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.font.bold = True
            run.font.size = Pt(14)

doc.add_paragraph() # spacing

# Details
p_details = doc.add_paragraph()
p_details.alignment = WD_ALIGN_PARAGRAPH.RIGHT
p_details.add_run("التاريخ: الانطلاق يوم الاحد تاريخ 9 / 4 / 1448 هـ\n").bold = True
p_details.add_run("المدة: خمسة أسابيع\n").bold = True
p_details.add_run("الوقت: 30 ساعة تدريبية - ثلاثة أيام بالأسبوع - 4:30 عصرا إلى 6:30 مساءً\n").bold = True

doc.add_paragraph() # spacing

# Pricing
p_price = doc.add_paragraph()
p_price.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p_price.add_run("السعر الأساسي: 949 ريال\n")
run.font.strike = True
run.font.color.rgb = RGBColor(217, 111, 99)

run = p_price.add_run("التسجيل المبكر: 749 ريال\n")
run.font.bold = True
run.font.size = Pt(18)
run.font.color.rgb = RGBColor(220, 176, 69)

# Contact
p_contact = doc.add_paragraph()
p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p_contact.add_run("للتسجيل: 0553811717\n")
run.font.bold = True
run.font.size = Pt(20)

doc.save("e:/MY PROJECT/Freelance Jobs/تصميم إعلان لدورة تدريبية/إعلان_الدورة_قابل_للتعديل.docx")
print("Word document generated successfully!")
