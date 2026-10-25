from playwright.sync_api import sync_playwright
import os, pymupdf, base64

with open('bg_4.jpg', 'rb') as f:
    bg4_b64 = base64.b64encode(f.read()).decode('utf-8')

html_path = os.path.abspath('index.html')
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1080, 'height': 1400})
    page.goto(f'file:///{html_path}')
    page.wait_for_timeout(1000)
    
    page.add_script_tag(url='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js')
    page.add_script_tag(url='https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js')
    
    js_code = f"""async () => {{
        const flyer = document.getElementById('flyer-card');
        const flyerClone = flyer.cloneNode(true);
        
        // Remove edit markers if any
        flyerClone.querySelectorAll('[contenteditable]').forEach(el => {{
            el.removeAttribute('contenteditable');
        }});
        
        const wrapper = document.createElement('div');
        wrapper.id = 'export-target';
        wrapper.style.position = 'fixed';
        wrapper.style.left = '-9999px';
        wrapper.style.top = '0';
        wrapper.style.width = '1080px';
        wrapper.style.minHeight = '1450px';
        wrapper.style.display = 'flex';
        wrapper.style.justifyContent = 'center';
        wrapper.style.alignItems = 'center';
        wrapper.style.padding = '40px 30px';
        wrapper.style.backgroundImage = 'linear-gradient(rgba(23, 39, 54, 0.25), rgba(23, 39, 54, 0.25)), url(\"data:image/jpeg;base64,{bg4_b64}\")';
        wrapper.style.backgroundRepeat = 'no-repeat';
        wrapper.style.backgroundPosition = 'center center';
        wrapper.style.backgroundSize = 'cover';
        
        wrapper.appendChild(flyerClone);
        document.body.appendChild(wrapper);
        
        const canvas = await html2canvas(wrapper, {{
            scale: 2,
            useCORS: true,
            logging: false
        }});
        
        document.body.removeChild(wrapper);
        
        const imgData = canvas.toDataURL('image/jpeg', 0.95);
        const {{ jsPDF }} = window.jspdf;
        const pdf = new jsPDF({{
            orientation: 'portrait',
            unit: 'px',
            format: [canvas.width / 2, canvas.height / 2]
        }});
        pdf.addImage(imgData, 'JPEG', 0, 0, canvas.width / 2, canvas.height / 2);
        return pdf.output('datauristring');
    }}"""
    
    pdf_base64 = page.evaluate(js_code)
    
    header, encoded = pdf_base64.split(',', 1)
    data = base64.b64decode(encoded)
    with open('test_with_bg.pdf', 'wb') as f:
        f.write(data)

    doc = pymupdf.open('test_with_bg.pdf')
    print('Pages count:', len(doc))
    page_pdf = doc[0]
    pix = page_pdf.get_pixmap(dpi=150)
    pix.save('test_with_bg_preview.png')
    print('Preview with background saved!')
    browser.close()
