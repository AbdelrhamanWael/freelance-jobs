import re
import os

with open('client_editor.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to move the background-image from body to #poster-canvas.
# And we need to make sure #poster-canvas has the exact aspect ratio/size of the background image, 
# so it matches perfectly.
# From previous tasks, the background image is 1622 x 2048, or we can just use width: 100% and aspect-ratio.
# Actually, the user said they wanted the client to edit and download.
# Let's just grab the CSS for body and #poster-canvas.
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
    
    # Let's ensure #poster-canvas has a fixed size so it scales nicely in html2pdf
    # Looking at the original coordinates (e.g. left: 56.6%, top: 12.3%), they are percentages!
    # Which means they will perfectly position themselves as long as #poster-canvas has the correct aspect ratio.
    # The original image is 1622 x 2048. Aspect ratio = 1622/2048 = 0.79199
    # Let's set a fixed width and height for #poster-canvas so html2pdf renders it properly.
    # We can set width: 800px; height: 1010px; for example.
    
    # In client_ad.html, what was the size of #poster-canvas? 
    # Let's just write this html out.
    with open('client_editor_fixed.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed background")
else:
    print("No background image found on body")
