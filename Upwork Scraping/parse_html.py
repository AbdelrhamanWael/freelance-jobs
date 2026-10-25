from bs4 import BeautifulSoup

with open('test_html.txt', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

articles = soup.find_all('article')
print(f'Found {len(articles)} articles')
for a in articles[:3]:
    print(a.get('class'))

sections = soup.select('section.up-card-section')
print(f'Found {len(sections)} sections')

job_tiles = soup.select('[data-test="job-tile"]')
print(f'Found {len(job_tiles)} job tiles by data-test')

print("Looking for title elements:")
for h2 in soup.find_all('h2')[:5]:
    print("H2:", h2.get_text(strip=True))

for h3 in soup.find_all('h3')[:5]:
    print("H3:", h3.get_text(strip=True))
