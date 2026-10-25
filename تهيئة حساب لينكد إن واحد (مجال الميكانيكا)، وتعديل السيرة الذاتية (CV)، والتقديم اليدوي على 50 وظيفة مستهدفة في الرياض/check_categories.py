import json
import os

# Load all job data
all_collected_jobs = []

json_files = [
    'linkedin_jobs_fleet_maintenance.json',
    'filtered_jobs_clean.json',
    'filtered_jobs.json'
]

for json_file in json_files:
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)
                all_collected_jobs.extend(jobs)
        except Exception as e:
            print(f'Error loading {json_file}: {e}')

# STRICT FILTERING RULES
def should_exclude_job(job):
    title = job.get('title', '').lower()
    company = job.get('company', '').lower()
    
    if 'technician' in title or 'technician' in company:
        return True
    if 'mechanic' in title and 'engineer' not in title:
        return True
    exclude_energy_terms = ['solar', 'pv', 'photovoltaic', 'substation', 'switchgear', 'transformers', 'electrical', 'renewable', 'wind', 'battery energy storage', 'bess']
    for term in exclude_energy_terms:
        if term in title or term in company:
            return True
    exclude_building_terms = ['water', 'pump', 'hvac', 'air conditioning', 'air-conditioning', 'cooling', 'mep', 'facility', 'facilities', 'data centre', 'data center', 'datacenter']
    for term in exclude_building_terms:
        if term in title or term in company:
            return True
    exclude_aviation_terms = ['aviation', 'aircraft', 'helicopter', 'avionics', 'airport', 'air compressors', 'airframe', 'powerplant', 'flight simulator', 'aoc', 'gaca']
    for term in exclude_aviation_terms:
        if term in title or term in company:
            return True
    if 'site engineer' in title:
        return True
    if 'bim' in title or 'cad' in title:
        return True
    exclude_irrelevant = ['golf', 'entertainment', 'hotel', 'turf', 'props']
    for term in exclude_irrelevant:
        if term in title or term in company:
            return True
    if 'apprentice' in title:
        return True
    if 'building systems' in company or 'real estate' in company:
        return True
    if 'foreman' in title:
        return True
    if 'sustainability' in title or 'ev charging' in title:
        return True
    return False

def categorize_job(job):
    title = job.get('title', '').lower()
    company = job.get('company', '').lower()
    
    fleet_keywords = ['fleet', 'rolling stock', 'rail', 'metro', 'train']
    heavy_equipment_keywords = ['heavy equipment', 'heavy machinery', 'earthmoving', 'excavator', 'bulldozer']
    automotive_keywords = ['automotive', 'auto', 'truck', 'bus', 'vehicle', 'commercial vehicle']
    
    for keyword in fleet_keywords:
        if keyword in title or keyword in company:
            return 'Fleet/Rail'
    for keyword in heavy_equipment_keywords:
        if keyword in title or keyword in company:
            return 'Heavy Equipment'
    for keyword in automotive_keywords:
        if keyword in title or keyword in company:
            return 'Automotive'
    if 'field service' in title:
        return 'Field Service'
    if 'mechanical engineer' in title:
        return 'Mechanical'
    if 'maintenance engineer' in title or 'maintenance supervisor' in title:
        return 'Maintenance'
    if 'asset' in title or 'asset' in company:
        return 'Asset Management'
    if 'inspector' in title:
        return 'Inspection'
    if 'service manager' in title:
        return 'Service'
    if 'process engineer' in title:
        return 'Manufacturing'
    if 'technical manager' in title or 'technical support' in title:
        return 'Technical'
    if 'operations' in title:
        return 'Operations'
    if 'sap' in title or 'system engineer' in title:
        return 'Systems'
    if 'team leader' in title or 'lead' in title:
        return 'Leadership'
    return 'Other'

# Apply filtering and categorization
filtered_jobs = []
for job in all_collected_jobs:
    if not should_exclude_job(job):
        category = categorize_job(job)
        job['category'] = category
        filtered_jobs.append(job)

# Remove duplicates
seen_urls = set()
unique_jobs = []
for job in filtered_jobs:
    url = job.get('url', '')
    if url not in seen_urls:
        seen_urls.add(url)
        unique_jobs.append(job)

# Show jobs by category
category_jobs = {}
for job in unique_jobs:
    cat = job.get('category', 'Other')
    if cat not in category_jobs:
        category_jobs[cat] = []
    category_jobs[cat].append(job)

# Save to file instead of printing to avoid Unicode errors
with open('category_check.txt', 'w', encoding='utf-8') as f:
    f.write('=' * 80 + '\n')
    f.write('JOBS BY CATEGORY:\n')
    f.write('=' * 80 + '\n')
    for cat, jobs in category_jobs.items():
        f.write(f'\n{cat} ({len(jobs)} jobs):\n')
        f.write('-' * 80 + '\n')
        for job in jobs:
            f.write(f"  - {job['title']} @ {job['company']}\n")

    f.write('\n' + '=' * 80 + '\n')
    f.write('OTHER CATEGORY (check these manually):\n')
    f.write('=' * 80 + '\n')
    if 'Other' in category_jobs:
        for job in category_jobs['Other']:
            f.write(f"  - {job['title']} @ {job['company']}\n")
            f.write(f"    URL: {job['url']}\n")

print('Category check saved to category_check.txt')
