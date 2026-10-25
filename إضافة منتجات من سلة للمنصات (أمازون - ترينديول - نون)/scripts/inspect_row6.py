import sys, io, openpyxl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

wb = openpyxl.load_workbook('data/amazon_upload_ready_290_products_2026-09-13_drafts.xlsm', data_only=True)
ws = wb['Template']

cols = [2, 7, 8, 9, 10, 11, 23, 68, 96, 110, 111, 115, 116, 149]

print("Labels (Row 4):")
for c in cols:
    print(f"  Col {c} ({ws.cell(4, c).value}):")

print("\nRow 6 Values (Product 1):")
for c in cols:
    print(f"  Col {c} ({ws.cell(4, c).value}): {ws.cell(6, c).value}")

print("\nRow 7 Values (Product 2):")
for c in cols:
    print(f"  Col {c} ({ws.cell(4, c).value}): {ws.cell(7, c).value}")
