import undetected_chromedriver as uc
import time
import urllib.parse
from bs4 import BeautifulSoup

options = uc.ChromeOptions()
options.add_argument('--disable-gpu')
# options.add_argument('--headless') # keep headful to pass Cloudflare easier

driver = uc.Chrome(options=options)

try:
    url = 'https://www.upwork.com/nx/search/jobs/?q=' + urllib.parse.quote_plus('"Interior Design"') + '&sort=recency&page=1'
    print("Navigating to Upwork...")
    driver.get(url)
    
    print("Waiting for job-tile or cloudflare...")
    # wait up to 30 seconds
    for i in range(30):
        if "job-tile" in driver.page_source:
            print("Found job-tile!")
            break
        time.sleep(1)
    else:
        print("job-tile not found in 30s. Current title:", driver.title)

    html = driver.page_source
    with open('test_html_uc.txt', 'w', encoding='utf-8') as f:
        f.write(html)
        
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    print(f'Found {len(articles)} articles')
finally:
    driver.quit()
    print("Done.")
