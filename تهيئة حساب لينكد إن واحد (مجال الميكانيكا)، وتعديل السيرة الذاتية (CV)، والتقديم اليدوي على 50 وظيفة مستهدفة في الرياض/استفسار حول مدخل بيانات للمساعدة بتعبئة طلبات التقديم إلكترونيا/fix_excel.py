import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Load workbook
wb = openpyxl.load_workbook('JobSearchResults_Comprehensive_backup.xlsx')
ws = wb.active
ws.title = 'Internships'

# ==============================================================================
# 1. WHY THE COLUMNS SHIFTED RIGHT:
# The original export script wrote row 7 headers in Columns 1..13 (A..M).
# But when appending data rows (8..63), the script started at Column 14 (N)
# instead of Column 1 (A). This created a 13-column gap where A..M were empty.
#
# FIX: Move all values from Columns 14..26 (N..Z) into Columns 1..13 (A..M).
# ==============================================================================
for r in range(8, ws.max_row + 1):
    for c in range(1, 14):
        src_col = c + 13  # Column 14 (N) maps to Col 1 (A), etc.
        val = ws.cell(r, src_col).value
        if c == 13:  # Application / source URL
            ws.cell(r, c).value = 'Open LinkedIn Job'
            if val:
                ws.cell(r, c).hyperlink = str(val)
        else:
            ws.cell(r, c).value = val

# 2. Delete the old empty columns (N through Z / cols 14..26)
ws.delete_cols(14, 13)

# ==============================================================================
# 3. STYLING & PROFESSIONAL VISUAL DESIGN
# Matches the executive standard of AkramSaeedInternshipList.xlsx
# ==============================================================================
font_title = Font(name='Arial', size=14, bold=True, color='233C59')
font_meta_bold = Font(name='Arial', size=10, bold=True, color='1E293B')
font_meta = Font(name='Arial', size=10, bold=False, color='526277')
font_meta_italic = Font(name='Arial', size=9.5, italic=True, color='64748B')

header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='233C59', end_color='233C59', fill_type='solid')

data_font = Font(name='Arial', size=10, color='1E293B')
data_font_bold = Font(name='Arial', size=10, bold=True, color='0F172A')
link_font = Font(name='Arial', size=10, color='1762A8', underline='single')

fill_even = PatternFill(fill_type=None)  # Pure White
fill_odd = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')  # Soft tint

thin_side = Side(border_style='thin', color='E2E8F0')
data_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

header_border_side = Side(border_style='thin', color='1B2E44')
header_border = Border(left=header_border_side, right=header_border_side, top=header_border_side, bottom=header_border_side)

# 4. Format Metadata Rows (1 to 5)
ws.row_dimensions[1].height = 28
ws.row_dimensions[2].height = 20
ws.row_dimensions[3].height = 20
ws.row_dimensions[4].height = 20
ws.row_dimensions[5].height = 20
ws.row_dimensions[6].height = 12

ws.cell(1, 1).font = font_title
ws.cell(1, 1).alignment = Alignment(vertical='center')

ws.cell(2, 1).font = font_meta
ws.cell(2, 1).alignment = Alignment(vertical='center')

ws.cell(3, 1).font = font_meta_bold
ws.cell(3, 1).alignment = Alignment(vertical='center')

ws.cell(4, 1).font = font_meta
ws.cell(4, 1).alignment = Alignment(vertical='center')

ws.cell(5, 1).font = font_meta_italic
ws.cell(5, 1).alignment = Alignment(vertical='center')

# 5. Format Header Row (7)
ws.row_dimensions[7].height = 34
for c in range(1, 14):
    cell = ws.cell(7, c)
    cell.font = header_font
    cell.fill = header_fill
    cell.border = header_border
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# 6. Format Data Rows (8 to 63)
center_cols = {3, 5, 9, 10, 11, 12, 13}
for r in range(8, ws.max_row + 1):
    ws.row_dimensions[r].height = 42
    row_fill = fill_odd if r % 2 == 1 else fill_even
    for c in range(1, 14):
        cell = ws.cell(r, c)
        cell.fill = row_fill
        cell.border = data_border
        
        # Alignment
        h_align = 'center' if c in center_cols else 'left'
        cell.alignment = Alignment(horizontal=h_align, vertical='top', wrap_text=True)
        
        # Font
        if c == 1:
            cell.font = data_font_bold
        elif c == 13:
            cell.font = link_font
        else:
            cell.font = data_font

# 7. Column Widths (Generous padding so no text is squashed)
col_widths = {
    'A': 22.0,  # Employer
    'B': 48.0,  # Internship / program
    'C': 18.0,  # Priority
    'D': 25.0,  # Location
    'E': 14.0,  # Timing
    'F': 28.0,  # Listing type
    'G': 30.0,  # Why it fits your CV
    'H': 32.0,  # Eligibility / next step
    'I': 24.0,  # Employer sponsorship policy
    'J': 16.0,  # Listed deadline
    'K': 18.0,  # Application status
    'L': 16.0,  # Requisition / ID
    'M': 22.0   # Application / source
}
for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

# 8. Freeze Panes & AutoFilter
ws.freeze_panes = 'C8'
ws.auto_filter.ref = f'A7:M{ws.max_row}'

# 9. Page Setup for Landscape view
ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.views.sheetView[0].showGridLines = True

wb.save('JobSearchResults_Comprehensive.xlsx')
print('Successfully processed and saved JobSearchResults_Comprehensive.xlsx!')
