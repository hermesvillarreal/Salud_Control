# This file contains the updated generate_plots and health_data functions
# that query the new separate tables instead of health_records

# Replace lines 165-333 in app.py (generate_plots function)
GENERATE_PLOTS_FUNCTION = """
@app.route("/generate_plots")
@login_required
def generate_plots():
    user_id = current_user.id
    try:
        # Query separate tables
        # Weight data
        weight_query = text("SELECT date, weight FROM weight_records WHERE user_id = :user_id ORDER BY date")
        with engine.connect() as conn:
            weight_data = pd.read_sql_query(weight_query, conn, params={"user_id": user_id})
        
        # Blood pressure data
        bp_query = text("SELECT date, systolic as blood_pressure_sys, diastolic as blood_pressure_dia FROM blood_pressure_records WHERE user_id = :user_id ORDER BY date")
        with engine.connect() as conn:
           bp_data = pd.read_sql_query(bp_query, conn, params={"user_id": user_id})
        
        # Glucose data
        glucose_query = text("SELECT date, glucose_level FROM glucose_records WHERE user_id = :user_id ORDER BY date")
        with engine.connect() as conn:
            glucose_data = pd.read_sql_query(glucose_query, conn, params={"user_id": user_id})
        
        # Food data
        food_query = text("SELECT date, meals FROM food_records WHERE user_id = :user_id ORDER BY date")
        with engine.connect() as conn:
            food_data = pd.read_sql_query(food_query, conn, params={"user_id": user_id})
        
        # Generate plots
        plots = {}
        
        # Weight over time: use the last measurement of each day
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
                fig_bp.add_trace(go.Scatter(x=valid_sys["date"].values, y=valid_sys["blood_pressure_sys"].values, name="Sistólica", mode='lines+markers'))
                fig_bp.add_trace(go.Scatter(x=valid_dia["date"].values, y=valid_dia["blood_pressure_dia"].values, name="Diastólica", mode='lines+markers'))
                fig_bp.update_layout(title="Blood Pressure Over Time", yaxis_title='Presión (mmHg)')
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
                   fig_meals = px.bar(meals_df, x='date', y='grams', color='meal', title='Por día / Comida (g totales)')
                    plots['meals_by_day'] = fig_meals.to_json()

                if macro_rows:
                    macro_df = pd.DataFrame(list(macro_rows.values())).sort_values('date')
                    fig_macros = go.Figure()
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['protein'], name='Proteínas (g)'))
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['carbs'], name='Carbohidratos (g)'))
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['fat'], name='Grasas (g)'))
                    fig_macros.update_layout(barmode='stack', title='Macronutrientes por día (g)')
                    plots['macros_by_day'] = fig_macros.to_json()
            except Exception as e:
                plots['meals_by_day_error'] = str(e)
        
        return jsonify(plots)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

# Replace lines 486-559 in app.py (get_health_data function)
GET_HEALTH_DATA_FUNCTION = """
@app.route('/health_data', methods=['GET'])
@login_required
def get_health_data():
    try:
        # Query all separate tables and combine the data
        weight_query = text('''
            SELECT w.date, w.weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia, 
                   NULL as glucose_level, NULL as meals
            FROM weight_records w
            WHERE w.user_id = :user_id
        ''')
        
        bp_query = text('''
            SELECT b.date, NULL as weight, b.systolic as blood_pressure_sys, b.diastolic as blood_pressure_dia,
                   NULL as glucose_level, NULL as meals
            FROM blood_pressure_records b
            WHERE b.user_id = :user_id
        ''')
        
        glucose_query = text('''
            SELECT g.date, NULL as weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia,
                   g.glucose_level, NULL as meals
            FROM glucose_records g
            WHERE g.user_id = :user_id
        ''')
        
        food_query = text('''
            SELECT f.date, NULL as weight, NULL as blood_pressure_sys, NULL as blood_pressure_dia,
                   NULL as glucose_level, f.meals
            FROM food_records f
            WHERE f.user_id = :user_id
        ''')
        
        with engine.connect() as conn:
            weight_df = pd.read_sql_query(weight_query, conn, params={"user_id": current_user.id})
            bp_df = pd.read_sql_query(bp_query, conn, params={"user_id": current_user.id})
            glucose_df = pd.read_sql_query(glucose_query, conn, params={"user_id": current_user.id})
            food_df = pd.read_sql_query(food_query, conn, params={"user_id": current_user.id})
        
        # Combine all dataframes
        df = pd.concat([weight_df, bp_df, glucose_df, food_df], ignore_index=True)
        
        # Sort by date
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        
        # Add user info
        user = db.get(User, current_user.id) if hasattr(current_user, 'id') else current_user
        
        # Generate basic plots (use the generate_plots endpoint for consistency)
        plots = {}
        if not df.empty:
            # Parse meals JSON into dicts for the API response
            if 'meals' in df.columns:
                def parse_meals_cell(x):
                    try:
                        return json.loads(x) if isinstance(x, str) and x else x
                    except Exception:
                        return x
               df['meals'] = df['meals'].apply(parse_meals_cell)
        
        return jsonify({
            'status': 'success',
            'data': df.to_dict(orient='records'),
            'plots': plots
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
"""

print("Functions ready for replacement in app.py")
