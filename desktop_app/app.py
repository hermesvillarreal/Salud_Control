from flask import Flask, request, jsonify, render_template
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import openai
import sqlite3
import json

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI if API key is available
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')

# Database configuration
DB_PATH = os.getenv('DESKTOP_DB_PATH', 'desktop_health.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
            meals TEXT,
            notes TEXT,
            source TEXT,
            sync_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    # Ensure 'meals' column exists (migration for older DBs)
    try:
        c.execute("PRAGMA table_info(health_records)")
        cols = [row[1] for row in c.fetchall()]
        if 'meals' not in cols:
            c.execute("ALTER TABLE health_records ADD COLUMN meals TEXT")
            conn.commit()
    except Exception:
        # If anything goes wrong with migration, ignore and continue
        pass

    conn.close()

# Initialize database
init_db()

@app.route("/sync_data", methods=["POST"])
def sync_data():
    data = request.json
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Create or get user
        try:
            c.execute('INSERT INTO users (name, email, phone) VALUES (?, ?, ?)',
                     (data["name"], data["email"], data["phone"]))
            user_id = c.lastrowid
        except sqlite3.IntegrityError:
            c.execute('SELECT id FROM users WHERE email = ?', (data["email"],))
            user_id = c.fetchone()[0]
        
        # Add health records
        sync_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        source_device = data.get("device_id", "unknown")
        
        for record in data["records"]:
            # Normalize meals field: accept dict or JSON string or missing
            meals = record.get('meals') or record.get('meals_data') or record.get('meals_data_json')
            try:
                meals_json = json.dumps(meals) if meals is not None else None
            except Exception:
                # If meals already a JSON string, keep as is
                meals_json = meals if isinstance(meals, str) else None

            c.execute('''
                INSERT INTO health_records 
                (user_id, date, weight, blood_pressure_sys, blood_pressure_dia,
                 glucose_level, meals, notes, source, sync_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, record.get("date"), record.get("weight"),
                record.get("blood_pressure_sys"), record.get("blood_pressure_dia"),
                record.get("glucose_level"), meals_json, record.get("notes", ""),
                source_device, sync_date
            ))
        
        conn.commit()
        return jsonify({"status": "success", "user_id": user_id})
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
    finally:
        if 'conn' in locals():
            conn.close()

@app.route("/generate_plots/<int:user_id>")
def generate_plots(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get user records
        query = '''
            SELECT date, weight, blood_pressure_sys, blood_pressure_dia, glucose_level, meals
            FROM health_records
            WHERE user_id = ?
            ORDER BY date
        '''
        
        data = pd.read_sql_query(query, conn, params=(user_id,))

        print(data.head())
        
        if data.empty:
            return jsonify({"error": "No records found"}), 404
        
        # Generate plots
        plots = {}
        
        # Weight over time: use the last measurement of each day
        try:
            data['date'] = pd.to_datetime(data['date'])
            # ensure weight is numeric and drop invalid/zero values before aggregating
            data['weight'] = pd.to_numeric(data['weight'], errors='coerce')
            data = data.sort_values('date')
            data['date_only'] = data['date'].dt.date.astype(str)
            # drop rows without a valid positive weight to avoid plotting 0 or NaN
            valid_weights = data.dropna(subset=['weight'])
            valid_weights = valid_weights[valid_weights['weight'] > 0]
            if not valid_weights.empty:
                daily_weight = valid_weights.groupby('date_only', as_index=False).agg({'weight': 'last'})
                print('Daily weight data:\n', daily_weight)
                fig_weight = px.line(daily_weight, x='date_only', y='weight', title='Weight Over Time')
                #fig_weight.update_traces(mode='lines+markers')
                fig_weight.update_layout(yaxis_title='Peso (kg)')
                plots['weight'] = fig_weight.to_json()
            else:
                # fallback to raw data if no valid weights
                fig_weight = px.line(data, x="date", y="weight", title="Weight Over Time")
                #fig_weight.update_traces(mode='lines+markers')
                fig_weight.update_layout(yaxis_title='Peso (kg)')
                plots["weight"] = fig_weight.to_json()
        except Exception as e:
            # fallback to raw plot if anything goes wrong
            fig_weight = px.line(data, x="date", y="weight", title="Weight Over Time")
            #fig_weight.update_traces(mode='lines+markers')
            fig_weight.update_layout(yaxis_title='Peso (kg)')
            plots["weight"] = fig_weight.to_json()
        
        valid_sys = data.dropna(subset=['blood_pressure_sys']).reset_index(drop=True)
        valid_sys = valid_sys[valid_sys['blood_pressure_sys'] > 0].reset_index(drop=True)
        valid_sys['blood_pressure_sys'] = pd.to_numeric(valid_sys['blood_pressure_sys'], errors='coerce')
        valid_sys = valid_sys.dropna(subset=['blood_pressure_sys']).reset_index(drop=True)
    
        print('Daily Systolic data:\n', valid_sys[['date', 'blood_pressure_sys']])

        valid_dia = data.dropna(subset=['blood_pressure_dia']).reset_index(drop=True)
        valid_dia = valid_dia[valid_dia['blood_pressure_dia'] > 0].reset_index(drop=True)
        valid_dia['blood_pressure_dia'] = pd.to_numeric(valid_dia['blood_pressure_dia'], errors='coerce')
        valid_dia = valid_dia.dropna(subset=['blood_pressure_dia']).reset_index(drop=True)

        print('Daily Diastolic data:\n', valid_dia[['date', 'blood_pressure_dia']])

        # Blood pressure
        fig_bp = go.Figure()
        fig_bp.add_trace(go.Scatter(x=valid_sys["date"].values, y=valid_sys["blood_pressure_sys"].values, name="Sistólica", mode='lines+markers'))
        fig_bp.add_trace(go.Scatter(x=valid_dia["date"].values, y=valid_dia["blood_pressure_dia"].values, name="Diastólica", mode='lines+markers'))
        fig_bp.update_layout(title="Blood Pressure Over Time", yaxis_title='Presión (mmHg)')
        plots["blood_pressure"] = fig_bp.to_json()
        
        # Glucose levels
        valid_glu = data.dropna(subset=['glucose_level']).reset_index(drop=True)
        valid_glu = valid_glu[valid_glu['glucose_level'] > 0].reset_index(drop=True)
        valid_glu['glucose_level'] = pd.to_numeric(valid_glu['glucose_level'], errors='coerce')

        print('Daily Glucose data:\n', valid_glu[['date', 'glucose_level']])

        fig_glucose = px.line(valid_glu, x="date", y="glucose_level", title="Glucose Levels Over Time")
        fig_glucose.update_traces(mode='lines+markers')
        fig_glucose.update_layout(yaxis_title='Glucosa (mg/dL)')
        plots["glucose"] = fig_glucose.to_json()

        # Parse meals (stored as JSON text) and create aggregated dataframes
        try:
            # Ensure meals column exists
            if 'meals' in data.columns:
                # Build per-day-per-meal summed grams (protein+carbs+fat)
                meal_rows = []
                macro_rows = {}

                for idx, row in data.iterrows():
                    date = str(row['date']).split(' ')[0]
                    meals_cell = row.get('meals')
                    if not meals_cell or pd.isna(meals_cell):
                        continue
                    try:
                        meals = json.loads(meals_cell) if isinstance(meals_cell, str) else meals_cell
                    except Exception:
                        meals = meals_cell

                    # Initialize macro totals for the day
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

                        # accumulate per-day macros
                        macro_rows[date]['protein'] += p
                        macro_rows[date]['carbs'] += c
                        macro_rows[date]['fat'] += f

                if meal_rows:
                    meals_df = pd.DataFrame(meal_rows)
                    # Plot: grams per day by meal (stacked/grouped)
                    fig_meals = px.bar(meals_df, x='date', y='grams', color='meal', title='Por día / Comida (g totales)')
                    plots['meals_by_day'] = fig_meals.to_json()

                if macro_rows:
                    macro_df = pd.DataFrame(list(macro_rows.values())).sort_values('date')
                    # Plot: macronutrients over time (each nutrient as a separate line)
                    fig_macros = go.Figure()
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['protein'], name='Proteínas (g)'))
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['carbs'], name='Carbohidratos (g)'))
                    fig_macros.add_trace(go.Bar(x=macro_df['date'], y=macro_df['fat'], name='Grasas (g)'))
                    fig_macros.update_layout(barmode='stack', title='Macronutrientes por día (g)')
                    plots['macros_by_day'] = fig_macros.to_json()
        except Exception as e:
            # don't fail entire request if meal parsing/plotting fails
            plots['meals_by_day_error'] = str(e)
        
        return jsonify(plots)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

def basic_analysis(data):
    """Realiza un análisis básico de los datos de salud sin usar IA"""
    try:
        stats = {
            "weight": {
                "mean": data["weight"].mean(),
                "trend": "increasing" if data["weight"].diff().mean() > 0 else "decreasing"
            },
            "blood_pressure": {
                "sys_mean": data["blood_pressure_sys"].mean(),
                "dia_mean": data["blood_pressure_dia"].mean()
            },
            "glucose": {
                "mean": data["glucose_level"].mean(),
                "std": data["glucose_level"].std()
            }
        }
        
        analysis = f"""
        Análisis básico de salud:
        - Peso promedio: {stats['weight']['mean']:.1f}kg (Tendencia: {stats['weight']['trend']})
        - Presión arterial promedio: {stats['blood_pressure']['sys_mean']:.0f}/{stats['blood_pressure']['dia_mean']:.0f}
        - Glucosa promedio: {stats['glucose']['mean']:.1f} (Desviación estándar: {stats['glucose']['std']:.1f})
        """
        
        return {
            "statistics": stats,
            "analysis": analysis
        }
    except Exception as e:
        return {
            "error": f"Error en el análisis básico: {str(e)}"
        }

def save_local_report(data):
    """Guarda el reporte como un archivo local"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"health_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        
        return {
            "status": "success",
            "filename": filename,
            "message": f"Reporte guardado como {filename}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al guardar el reporte: {str(e)}"
        }

@app.route("/analyze/<int:user_id>")
def analyze_health_data(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get user records
        query = '''
            SELECT date, weight, blood_pressure_sys, blood_pressure_dia, glucose_level
            FROM health_records
            WHERE user_id = ?
            ORDER BY date
        '''
        
        data = pd.read_sql_query(query, conn, params=(user_id,))
        
        if data.empty:
            return jsonify({"error": "No records found"}), 404
            
        # Realizar análisis básico
        analysis_result = basic_analysis(data)
        
        # Si la API de OpenAI está disponible, agregar análisis de IA
        if openai_api_key:
            try:
                analysis_prompt = f"""
                Analyze the following health metrics:
                Weight: Mean {analysis_result['statistics']['weight']['mean']:.1f}kg, 
                       Trend: {analysis_result['statistics']['weight']['trend']}
                Blood Pressure: Mean {analysis_result['statistics']['blood_pressure']['sys_mean']:.0f}/
                              {analysis_result['statistics']['blood_pressure']['dia_mean']:.0f}
                Glucose: Mean {analysis_result['statistics']['glucose']['mean']:.1f}, 
                        Standard Deviation {analysis_result['statistics']['glucose']['std']:.1f}
                
                Provide a brief health analysis and recommendations.
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a health analysis assistant."},
                        {"role": "user", "content": analysis_prompt}
                    ]
                )
                analysis_result['ai_analysis'] = response.choices[0].message.content
            except Exception as e:
                analysis_result['ai_analysis'] = f"AI analysis unavailable: {str(e)}"
        
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()
    
    # Calculate basic statistics
    stats = {
        "weight": {
            "mean": data["weight"].mean(),
            "trend": "increasing" if data["weight"].diff().mean() > 0 else "decreasing"
        },
        "blood_pressure": {
            "sys_mean": data["blood_pressure_sys"].mean(),
            "dia_mean": data["blood_pressure_dia"].mean()
        },
        "glucose": {
            "mean": data["glucose_level"].mean(),
            "std": data["glucose_level"].std()
        }
    }
    
    # Generate AI analysis
    analysis_prompt = f"""
    Analyze the following health metrics:
    Weight: Mean {stats['weight']['mean']:.1f}kg, Trend: {stats['weight']['trend']}
    Blood Pressure: Mean {stats['blood_pressure']['sys_mean']:.0f}/{stats['blood_pressure']['dia_mean']:.0f}
    Glucose: Mean {stats['glucose']['mean']:.1f}, Standard Deviation {stats['glucose']['std']:.1f}
    
    Provide a brief health analysis and recommendations.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a health analysis assistant."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        ai_analysis = response.choices[0].message.content
    except Exception as e:
        ai_analysis = f"AI analysis unavailable: {str(e)}"
    
    return jsonify({
        "statistics": stats,
        "ai_analysis": ai_analysis
    })

import os
from dotenv import load_dotenv

load_dotenv()

def send_report(data):
    """Guarda el reporte localmente ya que WhatsApp no está configurado"""
    return save_local_report(data)

@app.route('/health_data', methods=['GET'])
def get_health_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Get all health data
        c.execute('''
            SELECT u.name, u.email, u.phone, h.date, h.weight, 
                   h.blood_pressure_sys, h.blood_pressure_dia, h.glucose_level, h.meals
            FROM users u
            JOIN health_records h ON u.id = h.user_id
        ''')
        
        data = c.fetchall()
        
        # Convert to DataFrame
        columns = ['name', 'email', 'phone', 'date', 'weight', 
                   'blood_pressure_sys', 'blood_pressure_dia', 'glucose_level', 'meals']
        df = pd.DataFrame(data, columns=columns)
        
        # Generate basic plots
        plots = {}
        if not df.empty:
            # Weight plot (last measurement per day)
            try:
                df['date'] = pd.to_datetime(df['date'])
                df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
                df = df.sort_values('date')
                df['date_only'] = df['date'].dt.date.astype(str)
                valid_weights = df.dropna(subset=['weight'])
                valid_weights = valid_weights[valid_weights['weight'] > 0]
                if not valid_weights.empty:
                    daily_df = valid_weights.groupby('date_only', as_index=False).agg({'weight': 'last'})
                    fig_weight = px.line(daily_df, x='date_only', y='weight', title='Weight Over Time')
                    fig_weight.update_traces(mode='lines+markers')
                    fig_weight.update_layout(yaxis_title='Peso (kg)')
                    plots['weight'] = fig_weight.to_json()
                else:
                    fig_weight = px.line(df, x='date', y='weight', title='Weight Over Time')
                    fig_weight.update_traces(mode='lines+markers')
                    fig_weight.update_layout(yaxis_title='Peso (kg)')
                    plots['weight'] = fig_weight.to_json()
            except Exception:
                fig_weight = px.line(df, x='date', y='weight', title='Weight Over Time')
                fig_weight.update_traces(mode='lines+markers')
                fig_weight.update_layout(yaxis_title='Peso (kg)')
                plots['weight'] = fig_weight.to_json()
            
            # Blood pressure plot
            fig_bp = px.line(df, x='date', y=['blood_pressure_sys', 'blood_pressure_dia'], 
                           title='Blood Pressure Over Time')
            plots['blood_pressure'] = fig_bp.to_json()
            
            # Glucose plot
            fig_glucose = px.line(df, x='date', y='glucose_level',
                                title='Glucose Levels Over Time')
            plots['glucose'] = fig_glucose.to_json()
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

if __name__ == "__main__":
    app.run(debug=True)