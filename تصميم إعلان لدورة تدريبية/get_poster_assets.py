import asyncio
import os
import json
from playwright.async_api import async_playwright

html_path = os.path.abspath("client_ad.html")

async def extract():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=1)
        file_url = f"file:///{html_path.replace(chr(92), '/')}"
        await page.goto(file_url, wait_until="networkidle")
        
        # Get poster canvas
        poster = await page.query_selector("#poster-canvas")
        poster_box = await poster.bounding_box()
        
        # Extract text elements and their properties
        # We'll use JavaScript to iterate through all text nodes or specific classes
        items = await page.evaluate('''() => {
            const poster = document.querySelector('#poster-canvas');
            const rect = poster.getBoundingClientRect();
            
            // We want to capture anything that looks like text.
            // Let's just grab specific elements based on the HTML structure
            const elements = [
                ...poster.querySelectorAll('h1, h2, h3, p, span, div.text-center, div.text-right')
            ];
            
            const results = [];
            for (const el of elements) {
                // Only consider elements that have direct text content and no block children, or are specific targets
                let hasText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
                if (hasText) {
                    const elRect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    // Get coordinates relative to the poster
                    results.push({
                        text: el.innerText.trim(),
                        x: elRect.left - rect.left,
                        y: elRect.top - rect.top,
                        width: elRect.width,
                        height: elRect.height,
                        fontSize: style.fontSize,
                        color: style.color,
                        fontWeight: style.fontWeight,
                        textAlign: style.textAlign
                    });
                }
            }
            return results;
        }''')
        
        with open('poster_texts.json', 'w', encoding='utf-8') as f:
            json.dump({'poster_size': poster_box, 'texts': items}, f, ensure_ascii=False, indent=2)
            
        # Now hide all text elements to take a clean background screenshot
        await page.evaluate('''() => {
            const poster = document.querySelector('#poster-canvas');
            const elements = [
                ...poster.querySelectorAll('h1, h2, h3, p, span')
            ];
            for (const el of elements) {
                el.style.opacity = '0'; // hide text but keep layout
            }
            // Also hide SVG icons if they are part of the text
            const icons = poster.querySelectorAll('svg');
            for (const icon of icons) {
                icon.style.opacity = '0';
            }
        }''')
        
        await poster.screenshot(path="poster_bg_clean.png")
        
        await browser.close()
        print("Done capturing assets.")

if __name__ == '__main__':
    asyncio.run(extract())
