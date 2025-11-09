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
            notes TEXT,
            source TEXT,
            sync_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
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
            c.execute('''
                INSERT INTO health_records 
                (user_id, date, weight, blood_pressure_sys, blood_pressure_dia,
                 glucose_level, notes, source, sync_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, record["date"], record["weight"],
                record["blood_pressure_sys"], record["blood_pressure_dia"],
                record["glucose_level"], record.get("notes", ""),
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
            SELECT date, weight, blood_pressure_sys, blood_pressure_dia, glucose_level
            FROM health_records
            WHERE user_id = ?
            ORDER BY date
        '''
        
        data = pd.read_sql_query(query, conn, params=(user_id,))
        
        if data.empty:
            return jsonify({"error": "No records found"}), 404
        
        # Generate plots
        plots = {}
        
        # Weight over time
        fig_weight = px.line(data, x="date", y="weight", title="Weight Over Time")
        plots["weight"] = fig_weight.to_json()
        
        # Blood pressure
        fig_bp = go.Figure()
        fig_bp.add_trace(go.Scatter(x=data["date"], y=data["blood_pressure_sys"],
                                   name="Systolic"))
        fig_bp.add_trace(go.Scatter(x=data["date"], y=data["blood_pressure_dia"],
                                   name="Diastolic"))
        fig_bp.update_layout(title="Blood Pressure Over Time")
        plots["blood_pressure"] = fig_bp.to_json()
        
        # Glucose levels
        fig_glucose = px.line(data, x="date", y="glucose_level",
                             title="Glucose Levels Over Time")
        plots["glucose"] = fig_glucose.to_json()
        
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
                   h.blood_pressure_sys, h.blood_pressure_dia, h.glucose_level
            FROM users u
            JOIN health_records h ON u.id = h.user_id
        ''')
        
        data = c.fetchall()
        
        # Convert to DataFrame
        columns = ['name', 'email', 'phone', 'date', 'weight', 
                   'blood_pressure_sys', 'blood_pressure_dia', 'glucose_level']
        df = pd.DataFrame(data, columns=columns)
        
        # Generate basic plots
        plots = {}
        if not df.empty:
            # Weight plot
            fig_weight = px.line(df, x='date', y='weight', title='Weight Over Time')
            plots['weight'] = fig_weight.to_json()
            
            # Blood pressure plot
            fig_bp = px.line(df, x='date', y=['blood_pressure_sys', 'blood_pressure_dia'], 
                           title='Blood Pressure Over Time')
            plots['blood_pressure'] = fig_bp.to_json()
            
            # Glucose plot
            fig_glucose = px.line(df, x='date', y='glucose_level',
                                title='Glucose Levels Over Time')
            plots['glucose'] = fig_glucose.to_json()
        
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