with open('e:/MY PROJECT/Machine Learning/Upwork Scraping/scrap.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace init_browser
old_init = '''def init_browser() -> ChromiumPage:
    co = ChromiumOptions().headless(HEADLESS)
    co.set_argument("--disable-blink-features=AutomationControlled")
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-dev-shm-usage")
    co.set_argument("--window-size=1440,900")
    co.set_argument("--lang=en-US")
    page = ChromiumPage(co)
    page.timeouts.page_load = 30
    return page'''

new_init = '''def init_browser() -> ChromiumPage:
    co = ChromiumOptions().headless(HEADLESS)
    co.set_argument("--disable-blink-features=AutomationControlled")
    co.set_argument("--no-sandbox")
    co.set_argument("--disable-dev-shm-usage")
    co.set_argument("--disable-gpu")
    co.set_argument("--blink-settings=imagesEnabled=false")
    co.set_argument("--window-size=1440,900")
    co.set_argument("--lang=en-US")
    page = ChromiumPage(co)
    page.timeouts.page_load = 30
    return page'''

code = code.replace(old_init, new_init)

# Replace pagination
old_pag = '''        for page_num in range(1, MAX_PAGES + 1):
            url = f"{base_url}&page={page_num}"
            log.info(f"──► Page {page_num}: {url}")
            page.get(url)

            try:
                page.ele(".job-tile", timeout=15)
                time.sleep(2)
            except Exception:
                log.warning(f"  Timeout on page {page_num}.")
                time.sleep(3)'''

new_pag = '''        for page_num in range(1, MAX_PAGES + 1):
            url = f"{base_url}&page={page_num}"
            
            if page_num == 1:
                log.info(f"──► Page {page_num}: {url}")
                page.get(url)
            else:
                log.info(f"──► Page {page_num}: Clicking 'Next' button...")
                try:
                    next_btn = page.ele("@data-test=pagination-next", timeout=3)
                    if next_btn and not next_btn.states.is_disabled:
                        next_btn.click()
                    else:
                        page.get(url)
                except Exception:
                    page.get(url)

            try:
                page.ele(".job-tile", timeout=15)
                time.sleep(2)
            except Exception:
                log.warning(f"  Timeout on page {page_num}.")
                time.sleep(3)'''

code = code.replace(old_pag, new_pag)

with open('e:/MY PROJECT/Machine Learning/Upwork Scraping/scrap.py', 'w', encoding='utf-8') as f:
    f.write(code)
