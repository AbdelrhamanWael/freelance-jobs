import pandas as pd

df = pd.read_excel('Amazon_Missing_Data_Guide.xlsx')

screen2_skus = [
    '709993335242-V2', '6287035695755-V2', '653871977003-V2', '609143662900-V2',
    '0653871228303-V2', '709993346798-V2', '700435974137-V2', '653998144975-V2',
    '653871977140-V2', '709993325195-V2', '653871977201-V2', '653871976945-V2',
    '0653998144968-V2', '609143663563-V2', '0653871976969-V2', '603787530779-V2',
    '0653998144449-V2', '6285049347567-V2', '0653871976761-V2', '609143663404-V2',
    '6287033293096-V2', '609143663365-V2', '0653998144551-V2', '653871977164-V2',
    '653871977096-V2'
]

with open('screen2_table.txt', 'w', encoding='utf-8') as f:
    for sku in screen2_skus:
        row = df[df['SKU'] == sku]
        if not row.empty:
            r = row.iloc[0]
            f.write(f"{r['SKU']}\t{r['اسم المنتج']}\t{r['Unit Count المطلوب كتابته']}\t{r['Unit Count Type المطلوب اختياره']}\n")
        else:
            # check salla directly
            f.write(f"{sku}\tUnknown\t1\tCount\n")

print('Done writing screen2_table.txt')
