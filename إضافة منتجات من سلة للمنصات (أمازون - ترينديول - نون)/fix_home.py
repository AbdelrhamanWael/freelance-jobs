import csv

with open(r'منصات_الرفع_النهائية\2_أمازون_Amazon\21_Amazon_HOME_FINAL_corrected.txt', 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f, delimiter='\t'))

new_rows = []
for r in rows:
    if r and r[0] == 'ABC123-V2':
        continue
    if r and '-V2' in str(r[0]) and len(r) > 2 and not r[2]:
        r[2] = '(Default) Create or Replace'
    new_rows.append(r)

with open(r'منصات_الرفع_النهائية\2_أمازون_Amazon\21_Amazon_HOME_FINAL_READY.txt', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(new_rows)
