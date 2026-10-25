import json
import re

with open('code_artifact (1).html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('poster_texts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Move background-image from body to #poster-canvas
body_bg_match = re.search(r'body\s*{[^}]*background-image:\s*(url\([^\)]+\));[^}]*}', html)
if body_bg_match:
    bg_url = body_bg_match.group(1)
    
    # Remove background from body
    html = re.sub(r'(body\s*{[^}]*)(background-image:[^;]+;)([^}]*})', r'\1\3', html)
    html = re.sub(r'(body\s*{[^}]*)(background-size:[^;]+;)([^}]*})', r'\1\3', html)
    html = re.sub(r'(body\s*{[^}]*)(background-position:[^;]+;)([^}]*})', r'\1\3', html)
    html = re.sub(r'(body\s*{[^}]*)(background-repeat:[^;]+;)([^}]*})', r'\1\3', html)
    
    # Add background to #poster-canvas
    poster_css_replacement = r'#poster-canvas { \n            background-image: ' + bg_url + r';\n            background-size: cover;\n            background-position: center;\n            overflow: hidden;\n'
    html = re.sub(r'#poster-canvas\s*{', poster_css_replacement, html)
else:
    print("Background image not found on body")


# 2. Replace the contents of #poster-canvas with absolutely positioned elements based on poster_texts.json
# First, let's find the boundaries of #poster-canvas
# We can just use string replacement for the div contents.
# Since it's hard to parse HTML with regex, we can use a simple trick: 
# Find <div id="poster-canvas" ...> and the matching </div>.
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
canvas = soup.find(id='poster-canvas')
if canvas:
    # Clear existing contents
    canvas.clear()
    
    # Set the style of the canvas so it acts as an absolute positioning container
    # The original poster_texts.json was based on width 500px, height 888.875px
    canvas['style'] = "position: relative; width: 500px; height: 888.875px; margin: 0 auto; " + canvas.get('style', '')
    
    # Remove flex classes from tailwind as we are using absolute positioning
    classes = canvas.get('class', [])
    classes = [c for c in classes if c not in ['flex', 'flex-col', 'items-center', 'justify-center']]
    canvas['class'] = classes
    
    # Add new text elements
    for i, item in enumerate(data['texts']):
        div = soup.new_tag('div')
        # Apply absolute positioning
        div['style'] = f"position: absolute; left: {item['x']}px; top: {item['y']}px; width: {item['width']}px; font-size: {item['fontSize']}; color: {item['color']}; font-weight: {item['fontWeight']}; text-align: {item['textAlign']}; outline: none; line-height: 1.2;"
        div['contenteditable'] = 'true'
        div['title'] = 'انقر للتعديل'
        div['class'] = ['hover:bg-white/10', 'transition-colors', 'rounded']
        div.string = item['text']
        canvas.append(div)
        
# 3. Add html2pdf library and change exportToImage() to generate PDF
html2pdf_script = soup.new_tag('script', src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js")
soup.head.append(html2pdf_script)

html_str = str(soup)

# Change exportToImage function logic
# We'll use a regex to replace the content of exportToImage() function
# The original function starts with `function exportToImage() {`
pdf_logic = """
function exportToImage() {
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
        jsPDF:        { unit: 'px', format: [500, 888.875], orientation: 'portrait' }
    };

    const btnText = document.getElementById('download-btn-text');
    const oldText = btnText.innerText;
    btnText.innerText = 'جاري التحميل...';

    html2pdf().set(opt).from(element).save().then(() => {
        btnText.innerText = oldText;
    });
}
"""
html_str = re.sub(r'function\s+exportToImage\(\)\s*{[\s\S]*?(?=\n\s*function|\n\s*<\/script>)', pdf_logic, html_str, count=1)

# Let's change the button text from PNG to PDF
html_str = html_str.replace('تحميل الإعلان (PNG)', 'تحميل الإعلان (PDF)')
html_str = html_str.replace('(PNG)', '(PDF)')

with open('final_client_app.html', 'w', encoding='utf-8') as f:
    f.write(html_str)

print("Created final_client_app.html")
