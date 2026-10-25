import sys, io, openpyxl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb = openpyxl.load_workbook('data/exports/amazon_drafts_completed_ready_to_upload.xlsm', data_only=True)
ws = wb['Template']

cols = [2, 7, 8, 10, 11, 23, 68, 96, 105, 110, 111, 115, 116, 149]

print("Row 7 Values in completed file:")
for c in cols:
    lbl = ws.cell(4, c).value
    val = ws.cell(7, c).value
    print(f"  Col {c} ({lbl}): {val}")

print("\nRow 8 Values in completed file:")
for c in cols:
    lbl = ws.cell(4, c).value
    val = ws.cell(8, c).value
    print(f"  Col {c} ({lbl}): {val}")
