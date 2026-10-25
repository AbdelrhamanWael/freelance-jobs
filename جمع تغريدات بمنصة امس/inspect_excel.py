import pandas as pd
import json

file_path = r'e:\MY PROJECT\Freelance Jobs\جمع تغريدات بمنصة امس\Combined_Sample_Data_All_Accounts.xlsx'
df = pd.read_excel(file_path)

info = {
    'columns': df.columns.tolist(),
    'sample': df.head(2).to_dict('records')
}

with open(r'e:\MY PROJECT\Freelance Jobs\جمع تغريدات بمنصة امس\columns_info.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=2)
