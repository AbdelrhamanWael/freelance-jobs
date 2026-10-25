import re

def extract_poster():
    with open('code_artifact (1).html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract head
    head_match = re.search(r'(<!DOCTYPE html>.*?</head>)', html, re.DOTALL | re.IGNORECASE)
    head_content = head_match.group(1) if head_match else ""

    # Extract body start
    body_match = re.search(r'(<body.*?>)', html, re.IGNORECASE)
    body_start = body_match.group(1) if body_match else "<body>"
    
    # We want to remove the 'edit-mode-on' class from body_start if it exists
    body_start = body_start.replace('edit-mode-on', '')
    
    # Extract poster canvas
    start_idx = html.find('<div id="poster-canvas"')
    if start_idx == -1:
        print("Could not find poster-canvas")
        return
        
    div_count = 0
    end_idx = start_idx
    for i in range(start_idx, len(html)):
        if html[i:i+4] == '<div':
            div_count += 1
        elif html[i:i+5] == '</div':
            div_count -= 1
            if div_count == 0:
                end_idx = i + 6
                break
                
    poster_content = html[start_idx:end_idx]
    
    # Create clean HTML
    clean_html = f"""{head_content}
{body_start}
    <main class="flex flex-col items-center justify-center p-4 min-h-screen">
        {poster_content}
    </main>
</body>
</html>"""

    # Remove contenteditable attributes so the client cannot accidentally edit it
    clean_html = clean_html.replace('contenteditable="true"', '')

    with open('client_ad.html', 'w', encoding='utf-8') as f:
        f.write(clean_html)
    print("Clean ad created successfully as client_ad.html")

extract_poster()
