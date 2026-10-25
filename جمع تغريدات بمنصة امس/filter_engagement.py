import pandas as pd
import json

file_path = r'e:\MY PROJECT\Freelance Jobs\جمع تغريدات بمنصة امس\Combined_Sample_Data_All_Accounts.xlsx'
df = pd.read_excel(file_path)

# Ensure numeric columns
for col in ['عدد الإعجابات', 'عدد التعليقات', 'عدد إعادة النشر']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Calculate Engagement
df['التفاعل الكلي'] = df['عدد الإعجابات'] + df['عدد التعليقات'] + df['عدد إعادة النشر']

# Filter high engagement (e.g. > 0 for now, but let's consider > mean or simply sort)
# Since we want "high engagement", let's filter those with engagement > 0 and sort
df_high = df[df['التفاعل الكلي'] > 0].sort_values(by='التفاعل الكلي', ascending=False).copy()

# Drop the temporary column if not needed, or keep it
output_path = r'e:\MY PROJECT\Freelance Jobs\جمع تغريدات بمنصة امس\High_Engagement_Tweets.xlsx'
df_high.to_excel(output_path, index=False)

# Get top 5 for preview
top_5 = df_high.head(5)[['الحساب', 'رابط التغريدة URL', 'التفاعل الكلي', 'النص المرجعي']].to_dict('records')

with open(r'e:\MY PROJECT\Freelance Jobs\جمع تغريدات بمنصة امس\top_5.json', 'w', encoding='utf-8') as f:
    json.dump({'total_high_engagement_tweets': len(df_high), 'top_5': top_5}, f, ensure_ascii=False, indent=2)
