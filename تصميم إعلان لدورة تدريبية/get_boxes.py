from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1763, 'height': 1377})
    html_path = os.path.abspath('index.html')
    page.goto('file:///' + html_path.replace('\\', '/'))
    page.wait_for_timeout(1000)
    
    container = page.query_selector('.flyer-container').bounding_box()
    print('Container:', container)
    
    elements = [
        ('.institute-name', 'Institute'),
        ('.course-title', 'Title'),
        ('.course-subtitle', 'Subtitle'),
        ('.badge-comprehensive', 'Badge'),
        ('.features-section', 'Features Box'),
        ('.trainers-section', 'Trainers Box'),
        ('.details-section', 'Details Box'),
        ('.pricing-section', 'Pricing Box'),
        ('.registration', 'Registration'),
        ('.slogan', 'Slogan')
    ]
    for sel, name in elements:
        el = page.query_selector(sel)
        if el:
            b = el.bounding_box()
            print(f"{name}: x={b['x']:.1f}, y={b['y']:.1f}, w={b['width']:.1f}, h={b['height']:.1f}")
    browser.close()
