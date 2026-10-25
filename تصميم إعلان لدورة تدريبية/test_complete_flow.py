from playwright.sync_api import sync_playwright
import os, pymupdf

html_path = os.path.abspath('index.html')
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1200, 'height': 1300})
    page.goto(f'file:///{html_path}')
    page.wait_for_timeout(1000)
    
    # 1. Take full screenshot of browser
    page.screenshot(path='final_index_with_bg4.png')
    
    # 2. Click download PDF button
    with page.expect_download() as download_info:
        page.click('#download-pdf-btn')
    
    download = download_info.value
    download.save_as('output_ad_with_bg.pdf')
    
    # 3. Verify PDF with PyMuPDF
    doc = pymupdf.open('output_ad_with_bg.pdf')
    print('PDF page count:', len(doc))
    page_pdf = doc[0]
    pix = page_pdf.get_pixmap(dpi=150)
    pix.save('final_pdf_with_bg_preview.png')
    print('Rendered PDF page to final_pdf_with_bg_preview.png successfully!')
    
    browser.close()
