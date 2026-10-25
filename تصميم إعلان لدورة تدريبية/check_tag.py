import re
with open('client_ad.html', 'r', encoding='utf-8') as f:
    text = f.read()
match = re.search(r'<div\s+id=[\'\"]poster-canvas[\'\"][^>]*>', text)
if match:
    print('poster-canvas tag:', match.group(0))
