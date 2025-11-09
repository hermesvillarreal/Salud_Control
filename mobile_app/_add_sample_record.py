from database import MobileDatabase
from datetime import datetime

def add_sample():
    db = MobileDatabase()
    meals = {
        'breakfast': {'protein': 20, 'carbs': 30, 'fat': 10},
        'morning_snack': {'protein': 0, 'carbs': 0, 'fat': 0},
        'lunch': {'protein': 40, 'carbs': 50, 'fat': 20},
        'afternoon_snack': {'protein': 0, 'carbs': 0, 'fat': 0},
        'dinner': {'protein': 30, 'carbs': 40, 'fat': 15},
        'post_dinner': {'protein': 0, 'carbs': 0, 'fat': 0}
    }
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.add_health_record(user_id=1, weight=70, blood_pressure_sys=120, blood_pressure_dia=80, glucose_level=95, notes='Registro de prueba', datetime_str=now, meals_data=meals)
    print('Registro de prueba agregado')

if __name__ == '__main__':
    add_sample()
