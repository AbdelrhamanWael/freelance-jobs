import time
from DrissionPage import ChromiumPage, ChromiumOptions
import urllib.parse

co = ChromiumOptions().headless(False)
co.set_argument('--disable-blink-features=AutomationControlled')
co.set_argument('--no-sandbox')
co.set_argument('--disable-dev-shm-usage')
co.set_argument('--disable-gpu')
co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')

co.set_argument('--disable-infobars')
co.set_argument('--disable-notifications')
co.set_argument('--disable-popup-blocking')

page = ChromiumPage(co)

# Try clearing cache first
page.get('https://www.upwork.com/robots.txt')
page.clear_cache()
time.sleep(2)

url = 'https://www.upwork.com/nx/search/jobs/?q=' + urllib.parse.quote_plus('"Interior Design"') + '&sort=recency&page=1'

print("Navigating to Upwork...")
page.get(url)

print("Waiting for job-tile or cloudflare...")
try:
    if page.ele('.job-tile', timeout=30):
        print("Found job-tile!")
    else:
        print("job-tile not found in 30s. Current title:", page.title)
except Exception as e:
    print("Exception waiting for job-tile:", e)
    
html = page.html
with open('test_html3.txt', 'w', encoding='utf-8') as f:
    f.write(html)
    
page.quit()
print("Done.")
