import pandas as pd
import numpy as np

# Load the main file
df = pd.read_excel('Combined_Sample_Data_All_Accounts.xlsx')

# 1. CLEANING THE DATA (استبعاد التغريدات الفارغة أو غير المكتملة)
# Drop rows with any NaN values
df_clean = df.dropna().copy()

# Ensure text column is treated as string and strip whitespaces
df_clean['النص المرجعي'] = df_clean['النص المرجعي'].astype(str).str.strip()

# Drop rows where text is empty, "لا يوجد", or suspiciously short (e.g., just a small word)
df_clean = df_clean[df_clean['النص المرجعي'] != ""]
df_clean = df_clean[df_clean['النص المرجعي'].str.lower() != "nan"]
df_clean = df_clean[df_clean['النص المرجعي'] != "لا يوجد"]
df_clean = df_clean[df_clean['النص المرجعي'].str.len() > 15]

# Optional: Drop rows where the text is JUST a URL
url_pattern = r'^https?://[^\s]+$'
df_clean = df_clean[~df_clean['النص المرجعي'].str.match(url_pattern)]

print(f"Original rows: {len(df)}, Cleaned rows: {len(df_clean)}")

# 2. SYSTEMATIC SAMPLING
def systematic_sample(df_sub, n):
    N = len(df_sub)
    if n >= N:
        return df_sub
    # Calculate interval
    k = N / n
    # Generate indices: 0, k, 2k, ..., (n-1)k
    indices = [int(i * k) for i in range(n)]
    return df_sub.iloc[indices]

samples = []

accounts_plan = {
    'USEmbassyCairo': 241,  # 100%
    'ChinaEmbKSA': 190,     # 100%
    'USAbilAraby': 366,     # 10%
    'CGTNArabic': 278,      # 10%
    'CENTCOMArabic': 170    # 20%
}

for account, target_n in accounts_plan.items():
    df_acc = df_clean[df_clean['الحساب'] == account]
    print(f"{account}: found {len(df_acc)} clean tweets, targeting {target_n}")
    
    if len(df_acc) > 0:
        sampled = systematic_sample(df_acc, target_n)
        print(f"   -> Sampled: {len(sampled)}")
        samples.append(sampled)

final_df = pd.concat(samples, ignore_index=True)
print("Total sampled:", len(final_df))

output_name = 'Filtered_Sample_1245_Tweets_Cleaned.xlsx'
final_df.to_excel(output_name, index=False)
print(f"Saved to {output_name}")
