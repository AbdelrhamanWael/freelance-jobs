import json
import Extractor

try:
    raw_items = json.load(open('raw_dump.json', encoding='utf-8'))
    df = Extractor.extract_fields(raw_items)
    df = Extractor.filter_by_date_range(df)
    df = Extractor.clean_dataframe(df)
    try:
        df.to_excel('test.xlsx', index=False, engine='openpyxl')
        with open('success.txt', 'w') as f:
            f.write("EXCEL SAVED SUCCESSFULLY")
    except Exception as e:
        with open('excel_error.txt', 'w', encoding='utf-8') as f:
            f.write(str(e))
            
except Exception as e:
    with open('general_error.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
