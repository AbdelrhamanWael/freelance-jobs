import openpyxl

wb = openpyxl.load_workbook('JobSearchResults_Final.xlsx')
ws = wb.active

for i in range(1, 11):
    print(f'Row {i}: {[cell.value for cell in ws[i]]}')
