import openpyxl

wb = openpyxl.load_workbook('AkramSaeedInternshipList.xlsx')
ws = wb.active

for i, row in enumerate(ws.iter_rows(max_row=15, values_only=True)):
    print(f'Row {i}:', row)
