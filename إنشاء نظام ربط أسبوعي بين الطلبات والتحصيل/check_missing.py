import sqlite3
import pandas as pd
conn = sqlite3.connect('finance_system.db')
max_snap = pd.read_sql_query('SELECT MAX(snapshot_id) FROM orders', conn).iloc[0,0]

missing_orders = ['226405547', '230258608', '228690895', '228667507', '228663806', '228631917', '228631533', '228500515', '228462410', '228425359', '228403760']
missing_orders_str = ', '.join([f"'{o}'" for o in missing_orders])

print('Checking if these orders exist in the orders table at all:')
query = f'''
SELECT order_id, snapshot_id, platform, payment_method, price, cost
FROM orders 
WHERE order_id IN ({missing_orders_str}) AND snapshot_id = {max_snap}
'''
print(pd.read_sql_query(query, conn))

print('\nChecking if these orders exist in collections:')
query_coll = f'''
SELECT order_id, snapshot_id, platform, collected_amount
FROM collections
WHERE order_id IN ({missing_orders_str}) AND snapshot_id = {max_snap}
'''
print(pd.read_sql_query(query_coll, conn).to_string())
