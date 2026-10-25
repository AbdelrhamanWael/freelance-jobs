"""
quick_test.py - Live link extraction test
Opens one Upwork search page, grabs first 3 cards, prints resolved links.
No AI calls. No Excel output. Just link verification.
"""
import io, sys, re, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions
import urllib.parse

# ── replicate the same helpers from scrap.py ──────────────────────────────────
def slugify(title):
    slug = re.sub(r'[^\w\s-]', '', title)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:80]

def normalize_upwork_link(raw_link, title=''):
    if not raw_link: return 'No link'
    raw_link = raw_link.strip()
    if not raw_link: return 'No link'

    def build_apply(token, job_title):
        if job_title:
            return f'https://www.upwork.com/freelance-jobs/apply/{slugify(job_title)}_{token}/'
        return f'https://www.upwork.com/freelance-jobs/apply/{token}/'

    if 'freelance-jobs/apply' in raw_link:
        return raw_link if raw_link.startswith('http') else f'https://www.upwork.com{raw_link}'

    m = re.search(r'(?:_|/jobs/)(~[0-9a-zA-Z]{16,})', raw_link)
    if m: return build_apply(m.group(1), title)

    m = re.search(r'[?&=](~[0-9a-zA-Z]{16,})', raw_link)
    if m: return build_apply(m.group(1), title)

    m = re.search(r'[?&]uid=([0-9]{8,})', raw_link)
    if m: return build_apply(f'~{m.group(1)}', title)

    if raw_link.startswith('/'): return f'https://www.upwork.com{raw_link}'
    if raw_link.startswith('http'): return raw_link
    return 'No link'

def extract_client_info(card):
    info = {'payment_verified': False, 'rating': 0.0, 'total_spent': 0, 'spent_raw': '$0 spent'}
    text = card.get_text(separator=' ', strip=True)
    if 'payment verified' in text.lower():
        info['payment_verified'] = True
    m = re.search(r'([0-9]\.[0-9])\s*(?:stars?)?', text)
    if m: info['rating'] = float(m.group(1))
    m = re.search(r'\$([0-9]+\.?[0-9]*)([KkMm]?)\+?\s*spent', text)
    if m:
        amount = float(m.group(1))
        mult = {'K':1000,'M':1_000_000}.get(m.group(2).upper(), 1)
        info['total_spent'] = int(amount * mult)
        info['spent_raw'] = m.group(0).strip()
    return info

# ── search URL (same 3 keywords) ─────────────────────────────────────────────
KEYWORDS = [
    '"Architectural Design" OR "Interior Design" OR "Floor Plan"',
    'AutoCAD OR Revit OR BIM',
    '"3D Rendering" OR "Architectural Visualization" OR "Exterior Rendering"',
]
encoded = urllib.parse.quote_plus(' OR '.join(KEYWORDS))
SEARCH_URL = f'https://www.upwork.com/nx/search/jobs/?q={encoded}&sort=recency&payment_verified=1'

# ── open browser ──────────────────────────────────────────────────────────────
print('\nOpening browser...')
co = ChromiumOptions().headless(False)
co.set_argument('--disable-blink-features=AutomationControlled')
co.set_argument('--no-sandbox')
co.set_argument('--disable-dev-shm-usage')
page = ChromiumPage(co)
page.timeouts.page_load = 30

try:
    page.get(SEARCH_URL)
    try:
        page.ele('.job-tile', timeout=15)
        time.sleep(2)
    except Exception:
        pass

    soup  = BeautifulSoup(page.html, 'html.parser')
    cards = soup.find_all('article', class_='job-tile') or soup.select('section.up-card-section')

    print(f'\nFound {len(cards)} job cards on page 1.\n')
    print('=' * 70)

    good_links = []

    for card in cards:
        title_elem = card.find('h2') or card.find('h3')
        if not title_elem: continue
        # Strip Upwork's <span class="highlight"> tags from title
        for span in title_elem.find_all('span'):
            span.unwrap()
        title    = title_elem.get_text(strip=True)
        link_tag = title_elem.find('a')
        raw      = link_tag['href'] if (link_tag and 'href' in link_tag.attrs) else ''
        resolved = normalize_upwork_link(raw, title)
        client   = extract_client_info(card)

        skip = (client['total_spent'] == 0)
        flag = '[SKIP - $0 spent]' if skip else '[OK]'

        print(f'  {flag}')
        print(f'  Title  : {title[:70]}')
        print(f'  Link   : {resolved}')
        print(f'  Client : verified={client["payment_verified"]}  '
              f'rating={client["rating"]}  spent={client["spent_raw"]}')
        print()

        if not skip and resolved != 'No link':
            good_links.append((title, resolved, client))

    print('=' * 70)
    if good_links:
        title, link, client = good_links[0]
        print('\n*** FIRST VALID LINK (ready to use) ***')
        print(f'  Title  : {title}')
        print(f'  Link   : {link}')
        print(f'  Client : {client["spent_raw"]} | rating {client["rating"]} | verified={client["payment_verified"]}')
    else:
        print('\nNo valid (non-zero-spent) jobs found on page 1.')

finally:
    page.quit()
