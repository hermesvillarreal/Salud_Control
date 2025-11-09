import sqlite3
import pandas as pd

DB_PATH = 'desktop_health.db'

conn = sqlite3.connect(DB_PATH)
query = '''
SELECT date, weight FROM health_records WHERE user_id = ? ORDER BY date
'''
try:
    df = pd.read_sql_query(query, conn, params=(1,))
    print('Raw rows:', len(df))
    print(df.head(20).to_string(index=False))
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['date_only'] = df['date'].dt.date.astype(str)
        daily = df.groupby('date_only', as_index=False).agg({'weight':'last'})
        print('\nDaily (last weight per day):')
        print(daily.to_string(index=False))
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
