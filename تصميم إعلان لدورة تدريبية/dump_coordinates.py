from playwright.sync_api import sync_playwright
import os
import json

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1763, 'height': 1377})
    html_path = os.path.abspath('index.html')
    page.goto('file:///' + html_path.replace('\\', '/'))
    page.wait_for_timeout(1000)
    
    items = []
    
    # 1. Header
    items.append({'name': 'institute', 'sel': '.institute-name', 'text': page.inner_text('.institute-name')})
    items.append({'name': 'title', 'sel': '.course-title', 'text': page.inner_text('.course-title')})
    items.append({'name': 'subtitle', 'sel': '.course-subtitle', 'text': page.inner_text('.course-subtitle')})
    items.append({'name': 'badge', 'sel': '.badge-comprehensive', 'text': page.inner_text('.badge-comprehensive')})
    
    # 2. Features list items
    lis = page.query_selector_all('.features-list li')
    for i, li in enumerate(lis):
        txt = li.inner_text().strip()
        b = li.bounding_box()
        items.append({'name': f'feature_{i+1}', 'box': b, 'text': txt})
        
    # 3. Trainers
    titles = page.query_selector_all('.section-title')
    for i, t in enumerate(titles):
        items.append({'name': f'trainer_title_{i+1}', 'box': t.bounding_box(), 'text': t.inner_text().strip()})
        
    trainer_cards = page.query_selector_all('.trainer-card')
    for i, c in enumerate(trainer_cards):
        items.append({'name': f'trainer_card_{i+1}', 'box': c.bounding_box(), 'text': c.inner_text().strip()})
        
    # 4. Details
    details = page.query_selector_all('.detail-box .content')
    for i, d in enumerate(details):
        items.append({'name': f'detail_{i+1}', 'box': d.bounding_box(), 'text': d.inner_text().strip()})
        
    # 5. Pricing
    p_norm = page.query_selector('.price-normal')
    items.append({'name': 'price_normal', 'box': p_norm.bounding_box(), 'text': p_norm.inner_text().strip()})
    p_early = page.query_selector('.price-early')
    items.append({'name': 'price_early', 'box': p_early.bounding_box(), 'text': p_early.inner_text().strip()})
    
    # 6. Registration & Slogan
    reg = page.query_selector('.registration')
    items.append({'name': 'registration', 'box': reg.bounding_box(), 'text': reg.inner_text().strip()})
    slogan = page.query_selector('.slogan')
    items.append({'name': 'slogan', 'box': slogan.bounding_box(), 'text': slogan.inner_text().strip()})
    
    # Add bounding boxes for items with selectors
    for it in items:
        if 'sel' in it:
            it['box'] = page.query_selector(it['sel']).bounding_box()
            
    with open('coordinates.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print('Coordinates saved to coordinates.json')
    browser.close()
