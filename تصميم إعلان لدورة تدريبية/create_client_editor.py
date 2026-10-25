import re
import os

with open('client_ad.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add html2pdf.js library
script_tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>'
if 'html2pdf' not in html:
    html = html.replace('</head>', f'    {script_tag}\n</head>')

# Add contenteditable="true" to text tags.
# We will just add it to tags like h1, h2, h3, p, span that are inside the poster canvas.
# Actually, the best way is to use regex or BeautifulSoup, but let's just do a simple replacement for this specific file structure.

# Let's use BeautifulSoup
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

poster = soup.find(id='poster-canvas')
if poster:
    # Make text elements editable
    for tag in poster.find_all(['h1', 'h2', 'h3', 'p', 'span']):
        if tag.string or list(tag.children):
            tag['contenteditable'] = 'true'
            tag['style'] = tag.get('style', '') + '; outline: none;'
            tag['title'] = 'انقر للتعديل'

    # Add a download button floating at the top left
    btn_html = """
    <div style="position: fixed; top: 20px; left: 20px; z-index: 1000; display: flex; gap: 10px;">
        <button onclick="downloadPDF()" style="background-color: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: none; font-family: 'Cairo', sans-serif;">
            <svg style="width: 20px; height: 20px; display: inline-block; vertical-align: middle; margin-left: 8px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
            تحميل الإعلان (PDF)
        </button>
    </div>
    <script>
        function downloadPDF() {
            const element = document.getElementById('poster-canvas');
            
            // Remove selection if any
            if (window.getSelection) {
                window.getSelection().removeAllRanges();
            }

            const opt = {
                margin:       0,
                filename:     'إعلان_الدورة.pdf',
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 3, useCORS: true },
                jsPDF:        { unit: 'px', format: [element.offsetWidth, element.offsetHeight], orientation: 'portrait' }
            };

            // Temporarily disable outlines for PDF generation
            const editables = element.querySelectorAll('[contenteditable]');
            editables.forEach(el => el.style.outline = 'none');

            html2pdf().set(opt).from(element).save().then(() => {
                // Restore if needed, but outline:none is already set
            });
        }
    </script>
    """
    
    # Insert the button and script inside body
    body = soup.find('body')
    button_soup = BeautifulSoup(btn_html, 'html.parser')
    body.insert(0, button_soup)

with open('client_editor.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("client_editor.html created successfully.")
