import sqlite3
import json
from datetime import datetime

class MobileDatabase:
    def __init__(self):
        self.db_path = "salud_control.db"
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT
            )
        ''')
        
        # Create health_records table
        c.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT NOT NULL,
                weight REAL,
                blood_pressure_sys INTEGER,
                blood_pressure_dia INTEGER,
                glucose_level REAL,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_user(self, name, email, phone):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (name, email, phone) VALUES (?, ?, ?)',
                     (name, email, phone))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def add_health_record(self, user_id, weight, blood_pressure_sys, 
                         blood_pressure_dia, glucose_level, notes=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        date = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('''
            INSERT INTO health_records 
            (user_id, date, weight, blood_pressure_sys, blood_pressure_dia, 
             glucose_level, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, weight, blood_pressure_sys, blood_pressure_dia,
              glucose_level, notes))
        
        conn.commit()
        conn.close()

    def get_user_records(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT date, weight, blood_pressure_sys, blood_pressure_dia, 
                   glucose_level, notes 
            FROM health_records 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,))
        
        records = c.fetchall()
        formatted_records = []
        
        for record in records:
            formatted_records.append({
                'date': record[0],
                'weight': record[1],
                'blood_pressure_sys': record[2],
                'blood_pressure_dia': record[3],
                'glucose_level': record[4],
                'notes': record[5] or ''
            })
        
        conn.close()
        return formatted_records

    def export_to_json(self, user_id):
        records = self.get_user_records(user_id)
        return json.dumps(records)