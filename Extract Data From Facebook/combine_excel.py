import pandas as pd

try:
    print("Loading Chinese Embassy data...")
    df_china = pd.read_excel("Chinese_Embassy_FB_Data.xlsx")
    
    print("Loading US Embassy data...")
    df_us = pd.read_excel("US_Embassy_Cairo_FB_Data.xlsx")
    
    print("Combining datasets...")
    df_combined = pd.concat([df_china, df_us], ignore_index=True)
    
    print("Saving to Combined_FB_Data.xlsx...")
    df_combined.to_excel("Combined_FB_Data.xlsx", index=False, engine="openpyxl")
    
    print(f"Successfully combined! Total rows: {len(df_combined)}")
    
except Exception as e:
    print(f"Error combining files: {e}")
