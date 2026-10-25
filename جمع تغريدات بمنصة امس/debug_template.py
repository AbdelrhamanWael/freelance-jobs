import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document

doc = Document("template.docx")
print("=== البحث عن كل tags في القالب ===")
for t_idx, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            if "{{" in cell.text:
                print(f"Table {t_idx}, Row {r_idx}, Col {c_idx}: {cell.text[:80]}")
