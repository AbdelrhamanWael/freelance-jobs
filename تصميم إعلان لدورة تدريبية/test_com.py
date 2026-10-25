import win32com.client as win32
import os
import pymupdf

word = win32.Dispatch('Word.Application')
word.Visible = False
try:
    doc = word.Documents.Add()

    # 1763 x 1377 at 150 dpi is 846.24 pt x 660.96 pt
    doc.PageSetup.PageWidth = 846.24
    doc.PageSetup.PageHeight = 660.96
    doc.PageSetup.TopMargin = 0
    doc.PageSetup.BottomMargin = 0
    doc.PageSetup.LeftMargin = 0
    doc.PageSetup.RightMargin = 0

    bg_path = os.path.abspath('exact_bg_template.png')
    # Add background picture behind text
    bg_shape = doc.Shapes.AddPicture(bg_path, LinkToFile=False, SaveWithDocument=True, Left=0, Top=0, Width=846.24, Height=660.96)
    bg_shape.WrapFormat.Type = 3 # wdWrapBehind

    # Add a test textbox
    tb = doc.Shapes.AddTextbox(1, 270, 80, 305, 30)
    tb.Fill.Visible = 0 # msoFalse
    tb.Line.Visible = 0 # msoFalse
    tb.TextFrame.MarginTop = 0
    tb.TextFrame.MarginBottom = 0
    tb.TextFrame.MarginLeft = 0
    tb.TextFrame.MarginRight = 0
    
    rng = tb.TextFrame.TextRange
    rng.Text = "معهد مئة وثمانون درجة العالي للتدريب"
    rng.Font.Name = "Cairo"
    rng.Font.Size = 13
    rng.Font.Bold = True
    rng.Font.Color.RGB = 0xA6A43B # BGR for #3ba4a6 (59, 164, 166) -> R=59, G=164, B=166 -> BGR = 166, 164, 59
    rng.ParagraphFormat.Alignment = 1 # wdAlignParagraphCenter
    rng.ParagraphFormat.ReadingOrder = 0 # wdReadingOrderRtl

    test_docx = os.path.abspath('test_com_tb.docx')
    doc.SaveAs2(test_docx, FileFormat=16)
    test_pdf = os.path.abspath('test_com_tb.pdf')
    doc.SaveAs2(test_pdf, FileFormat=17)
    doc.Close(False)
finally:
    word.Quit()

print("Word COM test completed successfully!")

doc_pdf = pymupdf.open('test_com_tb.pdf')
print('PDF pages:', len(doc_pdf))
for i, page in enumerate(doc_pdf):
    pix = page.get_pixmap(dpi=150)
    pix.save(f'test_com_tb_p{i+1}.png')
print('Saved test_com_tb_p1.png')
