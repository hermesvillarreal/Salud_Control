import sqlite3
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

DB_PATH = 'desktop_health.db'

def test_generate_plots(user_id=1):
    conn = sqlite3.connect(DB_PATH)
    query = '''
        SELECT date, weight, blood_pressure_sys, blood_pressure_dia, glucose_level, meals
        FROM health_records
        WHERE user_id = ?
        ORDER BY date
    '''
    try:
        data = pd.read_sql_query(query, conn, params=(user_id,))
    except Exception as e:
        print('Error reading DB:', e)
        conn.close()
        return

    plots = {}
    if data.empty:
        print('No records')
        conn.close()
        return

    print('Got data rows:', len(data))
    # Weight
    fig_weight = px.line(data, x='date', y='weight', title='Weight Over Time')
    plots['weight'] = True

    # Glucose
    fig_glucose = px.line(data, x='date', y='glucose_level', title='Glucose')
    plots['glucose'] = True

    # Meals/macros
    meal_rows = []
    macro_rows = {}
    if 'meals' in data.columns:
        for idx, row in data.iterrows():
            date = str(row['date']).split(' ')[0]
            meals_cell = row.get('meals')
            if not meals_cell or pd.isna(meals_cell):
                continue
            try:
                meals = json.loads(meals_cell) if isinstance(meals_cell, str) else meals_cell
            except Exception:
                meals = meals_cell
            if date not in macro_rows:
                macro_rows[date] = {'date': date, 'protein': 0, 'carbs': 0, 'fat': 0}
            for meal_name, meal_data in (meals.items() if isinstance(meals, dict) else []):
                p = float(meal_data.get('protein', 0) or 0)
                c = float(meal_data.get('carbs', 0) or 0)
                f = float(meal_data.get('fat', 0) or 0)
                total_grams = p + c + f
                meal_rows.append({'date': date, 'meal': meal_name, 'grams': total_grams, 'protein': p, 'carbs': c, 'fat': f})
                macro_rows[date]['protein'] += p
                macro_rows[date]['carbs'] += c
                macro_rows[date]['fat'] += f

    print('meal_rows:', len(meal_rows))
    print('macro_rows:', len(macro_rows))
    if meal_rows:
        plots['meals_by_day'] = True
    if macro_rows:
        plots['macros_by_day'] = True

    print('Plots available:', list(plots.keys()))
    conn.close()

if __name__ == '__main__':
    test_generate_plots(1)
