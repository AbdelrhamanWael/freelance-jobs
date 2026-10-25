import json
import traceback
import sys
import Extractor

try:
    print("Loading json...")
    raw_items=json.load(open('raw_dump.json', encoding='utf-8'))
    print("Extracting fields...")
    df=Extractor.extract_fields(raw_items)
    print("Filtering date range...")
    df=Extractor.filter_by_date_range(df)
    print("Cleaning dataframe...")
    df=Extractor.clean_dataframe(df)
    print("Exporting to excel...")
    df.to_excel('test.xlsx', index=False, engine='openpyxl')
    print("Done!")
except Exception as e:
    print(f"Caught exception: {e}")
    with open('test_error.txt', 'w') as f:
        f.write(traceback.format_exc())
