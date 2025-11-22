#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update app.py functions to query separate tables
"""

import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Generate plots function replacement
new_generate_plots = '''@app.route("/generate_plots")
@login_required
def generate_plots():
    user_id = current_user.id
    try:
        # Query separate tables  
        weight_query = text("SELECT date, weight FROM weight_records WHERE user_id = :user_id ORDER BY date")
        bp_query = text("SELECT date, systolic as blood_pressure_sys, diastolic as blood_pressure_dia FROM blood_pressure_records WHERE user_id = :user_id ORDER BY date")
        glucose_query = text("SELECT date, glucose_level FROM glucose_records WHERE user_id = :user_id ORDER BY date")
        food_query = text("SELECT date, meals FROM food_records WHERE user_id = :user_id ORDER BY date")
        
        with engine.connect() as conn:
            weight_data = pd.read_sql_query(weight_query, conn, params={"user_id": user_id})
            bp_data = pd.read_sql_query(bp_query, conn, params={"user_id": user_id})
            glucose_data = pd.read_sql_query(glucose_query, conn, params={"user_id": user_id})
            food_data = pd.read_sql_query(food_query, conn, params={"user_id": user_id})
        
        # Generate plots
        plots = {}
        
        # Weight over time
        if not weight_data.empty:
            try:
                weight_data['date'] = pd.to_datetime(weight_data['date'])
                weight_data['weight'] = pd.to_numeric(weight_data['weight'], errors='coerce')
                weight_data = weight_data.sort_values('date')
                weight_data['date_only'] = weight_data['date'].dt.date.astype(str)
                valid_weights = weight_data.dropna(subset=['weight'])
                valid_weights = valid_weights[valid_weights['weight'] > 0]
                if not valid_weights.empty:
                    daily_weight = valid_weights.groupby('date_only', as_index=False).agg({'weight': 'last'})
                    daily_weight['weight'] = daily_weight['weight'].astype(float)
                    
                    min_weight = daily_weight['weight'].min()
                    max_weight = daily_weight['weight'].max()
                    weight_range = max_weight - min_weight
                    
                    if weight_range < 1:
                        y_min = min_weight - 5
                        y_max = max_weight + 5
                    else:
                        padding = weight_range * 0.1
                        y_min = min_weight - padding
                        y_max = max_weight + padding
                    
                    fig_weight = px.bar(daily_weight, x='date_only', y='weight', title='Weight Over Time', markers=True)
                    fig_weight.update_traces(
                        mode='lines+markers',
                        line=dict(color='#4CAF50', width=3),
                        marker=dict(size=10, color='#2E7D32', line=dict(width=2, color='white'))
                    )
                    fig_weight.update_layout(
                        yaxis_title='Peso (kg)',
                        xaxis_title='Fecha',
                        yaxis=dict(range=[y_min, y_max]),
                        hovermode='x unified',
                        plot_bgcolor='white',
                        font=dict(size=12)
                    )
                    plots['weight'] = fig_weight.to_json()
            except Exception as e:
                print(f"Error generating weight plot: {e}")
        
        # Blood pressure
        if not bp_data.empty:
            try:
                bp_data['date'] = pd.to_datetime(bp_data['date'])
                valid_sys = bp_data.dropna(subset=['blood_pressure_sys']).reset_index(drop=True)
                valid_sys = valid_sys[valid_sys['blood_pressure_sys'] > 0].reset_index(drop=True)
                valid_sys['blood_pressure_sys'] = pd.to_numeric(valid_sys['blood_pressure_sys'], errors='coerce')
                valid_sys = valid_sys.dropna(subset=['blood_pressure_sys']).reset_index(drop=True)
            
                valid_dia = bp_data.dropna(subset=['blood_pressure_dia']).reset_index(drop=True)
                valid_dia = valid_dia[valid_dia['blood_pressure_dia'] > 0].reset_index(drop=True)
                valid_dia['blood_pressure_dia'] = pd.to_numeric(valid_dia['blood_pressure_dia'], errors='coerce')
                valid_dia = valid_dia.dropna(subset=['blood_pressure_dia']).reset_index(drop=True)

                fig_bp = go.Figure()
                fig_bp.add_trace(go.Scatter(x=valid_sys["date"].values, y=valid_sys["blood_pressure_sys"].values, name="Sist\u00f3lica", mode='lines+markers'))
                fig_bp.add_trace(go.Scatter(x=valid_dia["date"].values, y=valid_dia["blood_pressure_dia"].values, name="Diast\u00f3lica", mode='lines+markers'))
                fig_bp.update_layout(title="Blood Pressure Over Time", yaxis_title='Presi\u00f3n (mmHg)')
                plots["blood_pressure"] = fig_bp.to_json()
            except Exception as e:
                print(f"Error generating blood pressure plot: {e}")
        
        # Glucose levels
        if not glucose_data.empty:
            try:
                glucose_data['date'] = pd.to_datetime(glucose_data['date'])
                valid_glu = glucose_data.dropna(subset=['glucose_level']).reset_index(drop=True)
                valid_glu = valid_glu[valid_glu['glucose_level'] > 0].reset_index(drop=True)
                valid_glu['glucose_level'] = pd.to_numeric(valid_glu['glucose_level'], errors='coerce')

                fig_glucose = px.line(valid_glu, x="date", y="glucose_level", title="Glucose Levels Over Time")
                fig_glucose.update_traces(mode='lines+markers')
                fig_glucose.update_layout(yaxis_title='Glucosa (mg/dL)')
                plots["glucose"] = fig_glucose.to_json()
            except Exception as e:
                print(f"Error generating glucose plot: {e}")

        # Food/meals data
        if not food_data.empty:
            try:
                food_data['date'] = pd.to_datetime(food_data['date'])
                meal_rows = []
                macro_rows = {}

                for idx, row in food_data.iterrows():
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
                        if not isinstance(meal_data, dict):
                            continue
                        p = float(meal_data.get('protein', 0) or 0)
                        c = float(meal_data.get('carbs', 0) or 0)
                        f = float(meal_data.get('fat', 0) or 0)
                        total_grams = p + c + f
                        meal_rows.append({'date': date, 'meal': meal_name, 'grams': total_grams, 'protein': p, 'carbs': c, 'fat': f})

                        macro_rows[date]['protein'] += p
                        macro_rows[date]['carbs'] += c
                        macro_rows[date]['fat'] += f

                if meal_rows:
                    meals_df = pd.DataFrame(meal_rows)
                    fig_meals = px.bar(meals_df, x='date', y='grams', color='meal', title='Por d\u00eda / Comida (g totales)')
                    plots['meals_by_day'] = fig_meals.to_json()

                if macro_rows:
                    macro_df = pd.DataFrame(list(macro_rows.values())).sort_values('date')
                    fig_macros = go.Figure()
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['protein'], name='Prote\u00ednas (g)'))
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['carbs'], name='Carbohidratos (g)'))
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['fat'], name='Grasas (g)'))
                    fig_macros.update_layout(barmode='stack', title='Macronutrientes por d\u00eda (g)')
                    plots['macros_by_day'] = fig_macros.to_json()
            except Exception as e:
                plots['meals_by_day_error'] = str(e)
        
        return jsonify(plots)
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

# Find and replace generate_plots function
pattern = r'@app\.route\("/generate_plots"\).*?(?=\n@app\.route|def basic_analysis|\Z)'
content = re.sub(pattern, new_generate_plots + '\n\n', content, flags=re.DOTALL)

print("✓ Updated generate_plots function")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ app.py updated successfully!")
print("  - generate_plots() now queries weight_records, blood_pressure_records, glucose_records, food_records")
