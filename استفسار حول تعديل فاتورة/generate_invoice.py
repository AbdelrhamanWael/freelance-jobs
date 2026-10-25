import pypdf
import pypdfium2 as pdfium
import os
import argparse

def get_base_template_streams(template_pdf_path):
    """
    Extract vector graphics from template:
    - Lines 0 to 938: Top logo vector paths, central watermark vector paths, footer icon circles & vector shapes
    - Lines 949 to 961: Footer divider line, header divider line, EMC, Q
    """
    reader = pypdf.PdfReader(template_pdf_path)
    page = reader.pages[0]
    orig_stream = page['/Contents'].get_object().get_data().decode('latin1')
    lines = orig_stream.splitlines(True)
    part1 = ''.join(lines[:939])
    part2 = ''.join(lines[949:962])
    return reader, part1, part2

def create_invoice_0050(template_pdf_path, output_pdf_path, invoice_no='0052', order_date='Oct 8, 2026'):
    """
    Generates the invoice for the 4 commercial kitchen equipment items:
    1. Gas Range (IT-G4B-90) - 9,780.00 AED
    2. Upright Freezer (DF1200S/S) - 6,790.00 AED
    3. Vegetable Chiller (VC600S/S) - 4,500.00 AED
    4. Microwave Oven (MW-1000W) - 950.00 AED
    Total: 22,020.00 AED
    """
    reader, part1, part2 = get_base_template_streams(template_pdf_path)

    # Invoice overlay content
    overlay = f'''q
0.0 0.0 612.283 858.898 re
W
n
1 0 0 1 0 0 cm
0 0 0 rg
BT
/F1 12 Tf
14.4 TL
1 0 0 1 56.69291 731.3389 Tm
(Healthito for healthy MEALS) Tj
T*
ET
BT
/F1 9 Tf
10.8 TL
1 0 0 1 457.5351 733.3389 Tm
(Order Date\\072 {order_date}) Tj
T*
ET
BT
/F1 12 Tf
14.4 TL
1 0 0 1 56.69291 688.8193 Tm
(Invoice No\\056 {invoice_no}) Tj
T*
ET
0.101961 0.101961 0.180392 rg
n
56.69291 632.1263 498.8972 28.34646 re
f*
1 1 1 rg
BT
/F1 9.5 Tf
11.4 TL
1 0 0 1 65.51654 641.1972 Tm
(Pos) Tj
ET
BT
/F1 9.5 Tf
1 0 0 1 205.8513 641.1972 Tm
(Description) Tj
ET
BT
/F1 9.5 Tf
1 0 0 1 381.9327 641.1972 Tm
(Unit Price) Tj
ET
BT
/F1 9.5 Tf
1 0 0 1 449.4461 641.1972 Tm
(QTY) Tj
ET
BT
/F1 9.5 Tf
1 0 0 1 493.9304 641.1972 Tm
(Total \\050AED\\051) Tj
ET
'''

    items_data = [
        {
            'pos': '1',
            'title': 'Heavy duty Gas Range with 4 Burners',
            'lines': [
                'MODEL: IT-G4B-90',
                'Full Stainless Steel body, Cast iron grids, Safety valves.',
                'Made by: Italy.',
                'Dimensions: 800x900x850 mm.'
            ],
            'unit_price': '9,780.00',
            'qty': '1',
            'total': '9,780.00',
            'price_x': 384.45,
            'tot_x': 500.67
        },
        {
            'pos': '2',
            'title': 'Full S/S Two Door Upright Freezer, 1200 Liters',
            'lines': [
                'MODEL: DF1200S/S',
                'Electronic thermostat and Digital LED temp display.',
                'Temp: -18~-22\\260C; Power: 650W; R404a.',
                'Dimensions: 1340x810x2010 mm.'
            ],
            'unit_price': '6,790.00',
            'qty': '1',
            'total': '6,790.00',
            'price_x': 384.45,
            'tot_x': 500.67
        },
        {
            'pos': '3',
            'title': 'Single Door Vegetable Chiller',
            'lines': [
                'MODEL: VC600S/S',
                'Fan cooling system.',
                'Temp: +2~+10\\260C; Power: 350W; 230V 50Hz.',
                'Dimensions: 600x700x1950 mm.'
            ],
            'unit_price': '4,500.00',
            'qty': '1',
            'total': '4,500.00',
            'price_x': 384.45,
            'tot_x': 500.67
        },
        {
            'pos': '4',
            'title': 'Commercial Microwave Oven, Heavy duty',
            'lines': [
                'MODEL: MW-1000W',
                'Stainless steel interior & exterior, Digital control.',
                'Power: 1000W; Voltage: 230V 50Hz.',
                'Dimensions: 510x360x300 mm.'
            ],
            'unit_price': '950.00',
            'qty': '1',
            'total': '950.00',
            'price_x': 392.79,
            'tot_x': 509.01
        }
    ]

    row_tops = [632.1263, 558.0, 484.0, 410.0]
    dividers = [558.0, 484.0, 410.0, 336.0]

    for i, it in enumerate(items_data):
        top = row_tops[i]
        div = dividers[i]
        val_y = top - 37.0
        cm_y = div
        first_line_y = (top - 14.0) - cm_y

        overlay += f'''
0 0 0 rg
BT
/F1 10 Tf
12 TL
1 0 0 1 70.92079 {val_y:.2f} Tm
({it['pos']}) Tj
ET
BT
1 0 0 1 {it['price_x']:.2f} {val_y:.2f} Tm
({it['unit_price']}) Tj
ET
BT
1 0 0 1 456.4321 {val_y:.2f} Tm
({it['qty']}) Tj
ET
BT
1 0 0 1 {it['tot_x']:.2f} {val_y:.2f} Tm
({it['total']}) Tj
ET
q
1 0 0 1 99.2126 {cm_y:.2f} cm
q
BT
1 0 0 1 0 {first_line_y:.2f} Tm
13 TL
/F1 9.5 Tf
0 0 0 rg
<7f> Tj
( ) Tj
( ) Tj
({it['title']}) Tj
T*
12.51 0 Td
'''
        for sub in it['lines']:
            overlay += f'''({sub}) Tj
T*
'''
        overlay += f'''-12.51 0 Td
ET
Q
Q
0.8 0.8 0.8 RG
0.4 w
n
56.69291 {div:.2f} m
555.5901 {div:.2f} l
S
'''

    # Total section and signatures
    overlay += f'''
BT
/F1 11 Tf
13.2 TL
ET
0 0 0 rg
BT
1 0 0 1 436.535 313.00 Tm
(Total) Tj
ET
BT
/F2 11 Tf
13.2 TL
ET
BT
1 0 0 1 490.86 313.00 Tm
(22,020.00) Tj
ET
BT
/F1 10 Tf
12 TL
ET
BT
1 0 0 1 56.69291 265.00 Tm
(Salesman) Tj
ET
BT
1 0 0 1 306.1415 265.00 Tm
(Customer) Tj
ET
BT
/F1 10 Tf
12 TL
ET
BT
1 0 0 1 56.69291 248.00 Tm
(\\205\\205\\205\\205\\205\\205\\205\\205\\205\\205\\056) Tj
ET
BT
1 0 0 1 306.1415 248.00 Tm
(\\205\\205\\205\\205\\205\\205\\205\\205\\205\\205\\056) Tj
ET
1 1 1 rg
n
138.5441 30.508 119.0859 13 re
f*
0.101961 0.101961 0.180392 rg
BT
/F2 9 Tf
10.8 TL
ET
BT
1 0 0 1 141.5441 33.508 Tm
(0 0 9 7 1 5 0 7 0 5 8 8 0 0) Tj
ET
1 1 1 rg
n
286.5 29.848 243.26 13 re
f*
0.101961 0.101961 0.180392 rg
BT
/F1 9 Tf
10.8 TL
ET
BT
1 0 0 1 289.5 32.848 Tm
(telegraph\\056store2\\100gmail\\056com) Tj
ET
Q
'''

    full_stream = (part1 + part2 + overlay).encode('latin1')

    writer = pypdf.PdfWriter()
    p = reader.pages[0]
    p['/Contents'].get_object().set_data(full_stream)
    writer.add_page(p)

    with open(output_pdf_path, 'wb') as f:
        writer.write(f)

    print(f"Successfully generated {output_pdf_path}")

def create_invoice_0049(template_pdf_path, output_pdf_path, invoice_no='0049', order_date='Sep 8, 2026'):
    """Retains previous 2-item invoice generation (DZ-300 + GEMM freezer)"""
    reader, part1, part2 = get_base_template_streams(template_pdf_path)

    overlay = f'''q
0.0 0.0 612.283 858.898 re
W
n
1 0 0 1 0 0 cm
BT
/F1 12 Tf
14.4 TL
ET
BT
/F1 12 Tf
14.4 TL
ET
0 0 0 rg
BT
1 0 0 1 56.69291 731.3389 Tm
(Healthito for healthy MEALS) Tj
T*
ET
BT
/F1 9 Tf
10.8 TL
ET
BT
1 0 0 1 457.5351 733.3389 Tm
(Order Date\\072 {order_date}) Tj
T*
ET
BT
/F1 12 Tf
14.4 TL
ET
BT
1 0 0 1 56.69291 688.8193 Tm
(Invoice No\\056 {invoice_no}) Tj
T*
ET
0.101961 0.101961 0.180392 rg
n
56.69291 632.1263 498.8972 28.34646 re
f*
1 1 1 rg
BT
/F1 9.5 Tf
11.4 TL
ET
BT
1 0 0 1 65.51654 641.1972 Tm
(Pos) Tj
T*
ET
BT
1 0 0 1 205.8513 641.1972 Tm
(Description) Tj
T*
ET
BT
1 0 0 1 381.9327 641.1972 Tm
(Unit Price) Tj
T*
ET
BT
1 0 0 1 449.4461 641.1972 Tm
(QTY) Tj
T*
ET
BT
1 0 0 1 493.9304 641.1972 Tm
(Total \\050AED\\051) Tj
T*
ET
0 0 0 rg
BT
/F1 10 Tf
12 TL
ET
BT
1 0 0 1 70.92079 603.1263 Tm
(1) Tj
T*
ET
BT
1 0 0 1 384.4492 603.1263 Tm
(2,625\\05600) Tj
T*
ET
BT
1 0 0 1 456.4321 603.1263 Tm
(1) Tj
T*
ET
BT
1 0 0 1 500.6697 603.1263 Tm
(2,625\\05600) Tj
T*
ET
q
1 0 0 1 99.2126 587.1263 cm
q
BT
1 0 0 1 0 29 Tm
13 TL
/F1 9.5 Tf
0 0 0 rg
<7f> Tj
( ) Tj
( ) Tj
(Vacuum Packing Machine) Tj
T*
12.51 0 Td
(MODEL: DZ\\055300) Tj
T*
(Power: 0\\05618kw / Voltage: 220V\\05550Hz) Tj
T*
-12.51 0 Td
ET
Q
Q
0.8 0.8 0.8 RG
0.4 w
n
56.69291 574.1263 m
555.5901 574.1263 l
S
0 0 0 rg
BT
/F1 10 Tf
12 TL
ET
BT
1 0 0 1 70.92079 545.1263 Tm
(2) Tj
T*
ET
BT
1 0 0 1 384.4492 545.1263 Tm
(6,890\\05600) Tj
T*
ET
BT
1 0 0 1 456.4321 545.1263 Tm
(1) Tj
T*
ET
BT
1 0 0 1 500.6697 545.1263 Tm
(6,890\\05600) Tj
T*
ET
q
1 0 0 1 99.2126 529.1263 cm
q
BT
1 0 0 1 0 29 Tm
13 TL
/F1 9.5 Tf
0 0 0 rg
<7f> Tj
( ) Tj
( ) Tj
(2 Door Freezer Cabinet) Tj
T*
12.51 0 Td
(Manufacturer: GEMM) Tj
T*
(MODEL: EFB/02) Tj
T*
-12.51 0 Td
ET
Q
Q
0.8 0.8 0.8 RG
0.4 w
n
56.69291 516.1263 m
555.5901 516.1263 l
S
BT
/F1 11 Tf
13.2 TL
ET
0 0 0 rg
BT
1 0 0 1 436.535 493.4491 Tm
(Total) Tj
T*
ET
BT
/F2 11 Tf
13.2 TL
ET
BT
1 0 0 1 498.8627 493.4491 Tm
(9,515\\05600) Tj
T*
ET
BT
/F1 10 Tf
12 TL
ET
BT
1 0 0 1 56.69291 283.8586 Tm
(Salesman) Tj
T*
ET
BT
1 0 0 1 306.1415 283.8586 Tm
(Customer) Tj
T*
ET
BT
/F1 10 Tf
12 TL
ET
BT
1 0 0 1 56.69291 266.8508 Tm
(\\205\\205\\205\\205\\205\\205\\205\\205\\205\\205\\056) Tj
T*
ET
BT
1 0 0 1 306.1415 266.8508 Tm
(\\205\\205\\205\\205\\205\\205\\205\\205\\205\\205\\056) Tj
T*
ET
1 1 1 rg
n
138.5441 30.508 119.0859 13 re
f*
0.101961 0.101961 0.180392 rg
BT
/F2 9 Tf
10.8 TL
ET
BT
1 0 0 1 141.5441 33.508 Tm
(0 0 9 7 1 5 0 7 0 5 8 8 0 0) Tj
T*
ET
1 1 1 rg
n
286.5 29.848 243.26 13 re
f*
0.101961 0.101961 0.180392 rg
BT
/F1 9 Tf
10.8 TL
ET
BT
1 0 0 1 289.5 32.848 Tm
(telegraph\\056store2\\100gmail\\056com) Tj
T*
ET
Q
'''

    full_stream = (part1 + part2 + overlay).encode('latin1')

    writer = pypdf.PdfWriter()
    p = reader.pages[0]
    p['/Contents'].get_object().set_data(full_stream)
    writer.add_page(p)

    with open(output_pdf_path, 'wb') as f:
        writer.write(f)

    print(f"Successfully generated {output_pdf_path}")

def render_preview(pdf_path, png_path):
    doc = pdfium.PdfDocument(pdf_path)
    img = doc[0].render(scale=2).to_pil()
    img.save(png_path)
    print(f"Rendered preview saved as {png_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Telegraph Store Invoices')
    parser.add_argument('--invoice-no', default='0052', help='Invoice number (default: 0052)')
    parser.add_argument('--date', default='Oct 8, 2026', help='Order Date (default: Oct 8, 2026)')
    args = parser.parse_args()

    template = 'Invoice0034Finalv5.pdf'
    
    # Target 4-item invoice
    target_pdf = f'Invoice{args.invoice_no} - Gas Range + Freezer + Vegetable Chiller + Microwave.pdf'
    create_invoice_0050(template, target_pdf, invoice_no=args.invoice_no, order_date=args.date)
    render_preview(target_pdf, f'Invoice{args.invoice_no}_preview.png')
