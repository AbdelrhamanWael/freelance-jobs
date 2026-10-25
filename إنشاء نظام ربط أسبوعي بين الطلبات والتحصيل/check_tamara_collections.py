import sqlite3
import pandas as pd

conn = sqlite3.connect('finance_system.db')
max_snap = pd.read_sql_query('SELECT MAX(snapshot_id) FROM orders', conn).iloc[0,0]
print(f'Max snapshot: {max_snap}')

# Get actual Tamara collections regardless of if they joined
query = f"""
SELECT order_id, collected_amount, collection_date, is_return 
FROM collections 
WHERE snapshot_id={max_snap} AND platform='Tamara'
LIMIT 20
"""
df = pd.read_sql_query(query, conn)
print('\nTamara collections in DB:')
print(df.to_string())

query2 = f"""
SELECT o.order_id, o.price, c.collected_amount, o.cost, o.payment_method
FROM orders o 
LEFT JOIN collections c ON o.order_id = c.order_id AND c.snapshot_id = o.snapshot_id
WHERE o.snapshot_id = {max_snap} AND o.cost = 39.0 AND o.price = 99.0 AND c.collected_amount IS NULL
LIMIT 15
"""
df2 = pd.read_sql_query(query2, conn)
print('\nUnpaid orders with cost=39, price=99 (Net profit -25.83 context):')
print(df2.to_string())
