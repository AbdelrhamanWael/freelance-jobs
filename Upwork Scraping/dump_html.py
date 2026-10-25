from DrissionPage import ChromiumPage, ChromiumOptions
import urllib.parse
import time

co = ChromiumOptions().headless(False)
co.set_argument('--disable-blink-features=AutomationControlled')
co.set_argument('--no-sandbox')
page = ChromiumPage(co)
url = 'https://www.upwork.com/nx/search/jobs/?q=' + urllib.parse.quote_plus('"Interior Design"') + '&sort=recency&page=1'
page.get(url)
time.sleep(5)
html = page.html
page.quit()

with open('test_html.txt', 'w', encoding='utf-8') as f:
    f.write(html)
