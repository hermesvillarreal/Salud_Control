import sqlite3
import os

# Path to the database
DB_PATH = 'salud_control.db' # It seems the app uses 'desktop_health.db' or 'salud_control.db' depending on context, let's check app.py or database.py
# Checking app.py, it imports SessionLocal from database.py.
# Checking database.py (I haven't read it yet, but list_dir showed it).
# Let's assume the DB is defined in database.py. I'll read it first to be sure.
# Actually, I'll just write a script that checks both or imports from database.py.

from database import engine
from sqlalchemy import text

def add_password_column():
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'password_hash' not in columns:
                print("Adding password_hash column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column password_hash already exists.")
                
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    add_password_column()
