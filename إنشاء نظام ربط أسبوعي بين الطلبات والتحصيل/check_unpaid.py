import sqlite3
import pandas as pd

conn = sqlite3.connect('finance_system.db')
max_snap = pd.read_sql_query('SELECT MAX(snapshot_id) FROM orders', conn).iloc[0,0]

query = f"""
SELECT o.order_id, o.payment_method, o.price, o.cost, o.shipping, o.commission, o.tax, c.collected_amount, c.collection_fee
FROM orders o
LEFT JOIN collections c ON o.order_id = c.order_id AND o.snapshot_id = c.snapshot_id
WHERE o.snapshot_id = {max_snap} 
"""
df = pd.read_sql_query(query, conn)
df['net_profit'] = df['collected_amount'].fillna(0) - (df['cost'].fillna(0) + df['shipping'].fillna(0) + df['commission'].fillna(0) + df['tax'].fillna(0) + df['collection_fee'].fillna(0))

unpaid = df[df['collected_amount'].isna() | (df['collected_amount'] == 0)]

print("Unpaid orders with Net Profit near -12.91:")
print(unpaid[abs(unpaid['net_profit'] + 12.91) < 0.1].head(15).to_string())

print("\nValue counts of payment methods for unpaid with -12.91 Net Profit:")
print(unpaid[abs(unpaid['net_profit'] + 12.91) < 0.1]['payment_method'].value_counts())
