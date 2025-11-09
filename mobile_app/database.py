import sqlite3
import json
from datetime import datetime

class MobileDatabase:
    def __init__(self):
        self.db_path = "salud_control.db"
        self.init_db()
        
        # Verificar si la estructura de la base de datos es correcta
        try:
            self.verify_db_structure()
        except Exception as e:
            print(f"Error en la estructura de la base de datos: {str(e)}")
            # Solo eliminar y recrear si hay un problema real
            import os
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            self.init_db()
            
    def verify_db_structure(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verificar la estructura de health_records
        c.execute("PRAGMA table_info(health_records)")
        columns = {column[1] for column in c.fetchall()}
        
        required_columns = {
            'id', 'user_id', 'datetime', 'weight', 'blood_pressure_sys',
            'blood_pressure_dia', 'glucose_level', 'notes',
            'breakfast_protein', 'breakfast_carbs', 'breakfast_fat',
            'morning_snack_protein', 'morning_snack_carbs', 'morning_snack_fat',
            'lunch_protein', 'lunch_carbs', 'lunch_fat',
            'afternoon_snack_protein', 'afternoon_snack_carbs', 'afternoon_snack_fat',
            'dinner_protein', 'dinner_carbs', 'dinner_fat',
            'post_dinner_protein', 'post_dinner_carbs', 'post_dinner_fat'
        }
        
        if not required_columns.issubset(columns):
            missing_columns = required_columns - columns
            raise Exception(f"Faltan columnas en health_records: {missing_columns}")
            
        conn.close()

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
        
        # Create general_info table
        c.execute('''
            CREATE TABLE IF NOT EXISTS general_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                age INTEGER,
                height REAL,
                initial_weight REAL,
                medical_condition TEXT,
                medication TEXT,
                main_objective TEXT,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Create nutrition_goals table
        c.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                objective TEXT NOT NULL,
                unit TEXT NOT NULL,
                quantity REAL NOT NULL,
                key_note TEXT,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create health_records table
        c.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                datetime TEXT NOT NULL,
                weight REAL,
                blood_pressure_sys INTEGER,
                blood_pressure_dia INTEGER,
                glucose_level REAL,
                breakfast_protein REAL,
                breakfast_carbs REAL,
                breakfast_fat REAL,
                morning_snack_protein REAL,
                morning_snack_carbs REAL,
                morning_snack_fat REAL,
                lunch_protein REAL,
                lunch_carbs REAL,
                lunch_fat REAL,
                afternoon_snack_protein REAL,
                afternoon_snack_carbs REAL,
                afternoon_snack_fat REAL,
                dinner_protein REAL,
                dinner_carbs REAL,
                dinner_fat REAL,
                post_dinner_protein REAL,
                post_dinner_carbs REAL,
                post_dinner_fat REAL,
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
                         blood_pressure_dia, glucose_level, notes="", datetime_str=None,
                         meals_data=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if datetime_str is None:
            datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if meals_data is None:
            meals_data = {
                'breakfast': {'protein': 0, 'carbs': 0, 'fat': 0},
                'morning_snack': {'protein': 0, 'carbs': 0, 'fat': 0},
                'lunch': {'protein': 0, 'carbs': 0, 'fat': 0},
                'afternoon_snack': {'protein': 0, 'carbs': 0, 'fat': 0},
                'dinner': {'protein': 0, 'carbs': 0, 'fat': 0},
                'post_dinner': {'protein': 0, 'carbs': 0, 'fat': 0}
            }
        
        c.execute('''
            INSERT INTO health_records 
            (user_id, datetime, weight, blood_pressure_sys, blood_pressure_dia, 
             glucose_level, 
             breakfast_protein, breakfast_carbs, breakfast_fat,
             morning_snack_protein, morning_snack_carbs, morning_snack_fat,
             lunch_protein, lunch_carbs, lunch_fat,
             afternoon_snack_protein, afternoon_snack_carbs, afternoon_snack_fat,
             dinner_protein, dinner_carbs, dinner_fat,
             post_dinner_protein, post_dinner_carbs, post_dinner_fat,
             notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, datetime_str, weight, blood_pressure_sys, blood_pressure_dia,
              glucose_level, 
              meals_data['breakfast']['protein'], meals_data['breakfast']['carbs'], meals_data['breakfast']['fat'],
              meals_data['morning_snack']['protein'], meals_data['morning_snack']['carbs'], meals_data['morning_snack']['fat'],
              meals_data['lunch']['protein'], meals_data['lunch']['carbs'], meals_data['lunch']['fat'],
              meals_data['afternoon_snack']['protein'], meals_data['afternoon_snack']['carbs'], meals_data['afternoon_snack']['fat'],
              meals_data['dinner']['protein'], meals_data['dinner']['carbs'], meals_data['dinner']['fat'],
              meals_data['post_dinner']['protein'], meals_data['post_dinner']['carbs'], meals_data['post_dinner']['fat'],
              notes))
        
        conn.commit()
        conn.close()

    def get_last_record(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT datetime, weight, blood_pressure_sys, blood_pressure_dia, 
                   glucose_level, notes,
                   breakfast_protein, breakfast_carbs, breakfast_fat,
                   morning_snack_protein, morning_snack_carbs, morning_snack_fat,
                   lunch_protein, lunch_carbs, lunch_fat,
                   afternoon_snack_protein, afternoon_snack_carbs, afternoon_snack_fat,
                   dinner_protein, dinner_carbs, dinner_fat,
                   post_dinner_protein, post_dinner_carbs, post_dinner_fat
            FROM health_records 
            WHERE user_id = ? 
            ORDER BY datetime DESC
            LIMIT 1
        ''', (user_id,))
        
        record = c.fetchone()
        conn.close()
        
        if record:
            return {
                'datetime': record[0],
                'weight': record[1],
                'blood_pressure_sys': record[2],
                'blood_pressure_dia': record[3],
                'glucose_level': record[4],
                'notes': record[5],
                'meals': {
                    'breakfast': {'protein': record[6], 'carbs': record[7], 'fat': record[8]},
                    'morning_snack': {'protein': record[9], 'carbs': record[10], 'fat': record[11]},
                    'lunch': {'protein': record[12], 'carbs': record[13], 'fat': record[14]},
                    'afternoon_snack': {'protein': record[15], 'carbs': record[16], 'fat': record[17]},
                    'dinner': {'protein': record[18], 'carbs': record[19], 'fat': record[20]},
                    'post_dinner': {'protein': record[21], 'carbs': record[22], 'fat': record[23]}
                }
            }
        return None

    def get_user_records(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT datetime, weight, blood_pressure_sys, blood_pressure_dia, 
                   glucose_level, notes,
                   breakfast_protein, breakfast_carbs, breakfast_fat,
                   morning_snack_protein, morning_snack_carbs, morning_snack_fat,
                   lunch_protein, lunch_carbs, lunch_fat,
                   afternoon_snack_protein, afternoon_snack_carbs, afternoon_snack_fat,
                   dinner_protein, dinner_carbs, dinner_fat,
                   post_dinner_protein, post_dinner_carbs, post_dinner_fat
            FROM health_records 
            WHERE user_id = ? 
            ORDER BY datetime DESC
        ''', (user_id,))

        records = c.fetchall()
        formatted_records = []

        for record in records:
            # build meals dict from columns
            meals = {
                'breakfast': {'protein': record[6], 'carbs': record[7], 'fat': record[8]},
                'morning_snack': {'protein': record[9], 'carbs': record[10], 'fat': record[11]},
                'lunch': {'protein': record[12], 'carbs': record[13], 'fat': record[14]},
                'afternoon_snack': {'protein': record[15], 'carbs': record[16], 'fat': record[17]},
                'dinner': {'protein': record[18], 'carbs': record[19], 'fat': record[20]},
                'post_dinner': {'protein': record[21], 'carbs': record[22], 'fat': record[23]}
            }

            formatted_records.append({
                'date': record[0],
                'datetime': record[0],
                'weight': record[1],
                'blood_pressure_sys': record[2],
                'blood_pressure_dia': record[3],
                'glucose_level': record[4],
                'notes': record[5] or '',
                'meals': meals
            })

        conn.close()
        return formatted_records

    def save_general_info(self, user_id, age, height, initial_weight, 
                        medical_condition, medication, main_objective):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Verificar si ya existe un registro para este usuario
        c.execute('SELECT id FROM general_info WHERE user_id = ?', (user_id,))
        existing_record = c.fetchone()
        
        if existing_record:
            # Actualizar registro existente
            c.execute('''
                UPDATE general_info
                SET age = ?, height = ?, initial_weight = ?, 
                    medical_condition = ?, medication = ?, 
                    main_objective = ?, last_updated = ?
                WHERE user_id = ?
            ''', (age, height, initial_weight, medical_condition, 
                  medication, main_objective, current_datetime, user_id))
        else:
            # Crear nuevo registro
            c.execute('''
                INSERT INTO general_info 
                (user_id, age, height, initial_weight, medical_condition, 
                 medication, main_objective, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, age, height, initial_weight, medical_condition,
                  medication, main_objective, current_datetime))
        
        conn.commit()
        conn.close()

    def get_general_info(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT age, height, initial_weight, medical_condition, 
                   medication, main_objective, last_updated
            FROM general_info 
            WHERE user_id = ?
        ''', (user_id,))
        
        record = c.fetchone()
        conn.close()
        
        if record:
            return {
                'age': record[0],
                'height': record[1],
                'initial_weight': record[2],
                'medical_condition': record[3],
                'medication': record[4],
                'main_objective': record[5],
                'last_updated': record[6]
            }
        return None

    def save_nutrition_goal(self, user_id, objective, unit, quantity, key_note):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Verificar si ya existe un objetivo para este usuario
        c.execute('''
            SELECT id FROM nutrition_goals 
            WHERE user_id = ? AND objective = ?
        ''', (user_id, objective))
        existing_goal = c.fetchone()
        
        if existing_goal:
            # Actualizar objetivo existente
            c.execute('''
                UPDATE nutrition_goals
                SET unit = ?, quantity = ?, key_note = ?, last_updated = ?
                WHERE user_id = ? AND objective = ?
            ''', (unit, quantity, key_note, current_datetime, user_id, objective))
        else:
            # Crear nuevo objetivo
            c.execute('''
                INSERT INTO nutrition_goals 
                (user_id, objective, unit, quantity, key_note, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, objective, unit, quantity, key_note, current_datetime))
        
        conn.commit()
        conn.close()

    def get_nutrition_goals(self, user_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT objective, unit, quantity, key_note, last_updated
            FROM nutrition_goals 
            WHERE user_id = ?
            ORDER BY id
        ''', (user_id,))
        
        goals = c.fetchall()
        conn.close()
        
        return [
            {
                'objective': goal[0],
                'unit': goal[1],
                'quantity': goal[2],
                'key_note': goal[3],
                'last_updated': goal[4]
            }
            for goal in goals
        ]

    def export_to_json(self, user_id):
        records = self.get_user_records(user_id)
        return json.dumps(records)