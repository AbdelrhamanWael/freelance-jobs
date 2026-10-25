import asyncio
import os
from playwright.async_api import async_playwright
from pdf2docx import Converter

html_path = os.path.abspath("client_ad.html")
pdf_path = os.path.abspath("poster_perfect.pdf")
docx_path = os.path.abspath("الإعلان_النهائي_القابل_للتعديل.docx")

async def html_to_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=2)
        file_url = f"file:///{html_path.replace(chr(92), '/')}"
        await page.goto(file_url, wait_until="networkidle")
        
        # Hide the body background and center the poster at 0,0
        await page.add_style_tag(content='''
            body { background: none !important; margin: 0 !important; padding: 0 !important; }
            main { padding: 0 !important; margin: 0 !important; align-items: flex-start !important; justify-content: flex-start !important; }
            #poster-canvas { transform: none !important; margin: 0 !important; border-radius: 0 !important; box-shadow: none !important; }
        ''')
        
        # Get poster canvas dimensions
        poster = await page.query_selector("#poster-canvas")
        box = await poster.bounding_box()
        
        width = f"{box['width']}px"
        height = f"{box['height']}px"
        
        await page.pdf(
            path=pdf_path, 
            print_background=True, 
            width=width, 
            height=height,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            page_ranges="1"
        )
        await browser.close()
        print("PDF generated successfully.")

def pdf_to_docx():
    if os.path.exists(pdf_path):
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        print("Word document generated successfully from PDF.")
    else:
        print("PDF file not found.")

if __name__ == '__main__':
    asyncio.run(html_to_pdf())
    pdf_to_docx()
