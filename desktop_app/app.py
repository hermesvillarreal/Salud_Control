from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
from database import SessionLocal, engine
from models import Base, User, HealthRecord, WeightRecord, BloodPressureRecord, GlucoseRecord, FoodRecord, ExerciseRecord
from sqlalchemy.orm import Session
from sqlalchemy import text
from services import get_or_create_user, create_health_record
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey") # Change this in production!

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        return db.get(User, int(user_id))
    finally:
        db.close()

# Load environment variables
load_dotenv()

# Initialize Gemini if API key is available
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Correo o contraseña incorrectos')
        finally:
            db.close()
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        db = SessionLocal()
        try:
            if db.query(User).filter(User.email == email).first():
                flash('El correo ya está registrado')
                return redirect(url_for('register'))
            
            new_user = User(name=name, email=email, phone=phone)
            new_user.set_password(password)
            db.add(new_user)
            db.commit()
            
            login_user(new_user)
            return redirect(url_for('index'))
        except Exception as e:
            db.rollback()
            flash(f'Error al registrar: {str(e)}')
        finally:
            db.close()
            
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')

# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)

# Initialize database
init_db()

@app.route("/sync_data", methods=["POST"])
def sync_data():
    # This endpoint might be used by external devices, so we might need API token auth later.
    # For now, we'll leave it as is but it won't be linked to the web session.
    # Ideally, the device sends a user identifier.
    data = request.json
    db = SessionLocal()
    
    try:
        # Create or get user
        user = get_or_create_user(db, data["email"], data["name"], data.get("phone"))
        
        # Add health records
        source_device = data.get("device_id", "unknown")
        
        for record in data["records"]:
            create_health_record(db, user.id, record, source_device)
        
        return jsonify({"status": "success", "user_id": user.id})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
    finally:
        db.close()

@app.route('/add_record', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'GET':
        return render_template('add_record.html')
    
    if request.method == 'POST':
        data = request.json
        db = SessionLocal()
        try:
            # Use current_user
            create_health_record(db, current_user.id, data, 'web_pwa')
            
            return jsonify({"status": "success"})
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
        finally:
            db.close()

@app.route('/add/weight', methods=['GET', 'POST'])
@login_required
def add_weight():
    if request.method == 'GET':
        return render_template('add_weight.html')
    
    if request.method == 'POST':
        data = request.json
        db = SessionLocal()
        try:
            from services import create_weight_record
            create_weight_record(db, current_user.id, data, 'web_pwa')
            return jsonify({"status": "success"})
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
        finally:
            db.close()

@app.route('/add/pressure', methods=['GET', 'POST'])
@login_required
def add_pressure():
    if request.method == 'GET':
        return render_template('add_pressure.html')
    
    if request.method == 'POST':
        data = request.json
        db = SessionLocal()
        try:
            from services import create_blood_pressure_record
            create_blood_pressure_record(db, current_user.id, data, 'web_pwa')
            return jsonify({"status": "success"})
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
        finally:
            db.close()

@app.route('/add/glucose', methods=['GET', 'POST'])
@login_required
def add_glucose():
    if request.method == 'GET':
        return render_template('add_glucose.html')
    
    if request.method == 'POST':
        data = request.json
        db = SessionLocal()
        try:
            from services import create_glucose_record
            create_glucose_record(db, current_user.id, data, 'web_pwa')
            return jsonify({"status": "success"})
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
        finally:
            db.close()

@app.route('/add/food', methods=['GET', 'POST'])
@login_required
def add_food():
    if request.method == 'GET':
        # Check for existing food records for today
        today_str = datetime.now().strftime('%Y-%m-%d')
        db = SessionLocal()
        preloaded_meals = None
        try:
            # Get the latest food record for today
            last_record = db.query(FoodRecord).filter(
                FoodRecord.user_id == current_user.id,
                FoodRecord.date.like(f"{today_str}%")
            ).order_by(FoodRecord.date.desc()).first()
            
            if last_record and last_record.meals:
                preloaded_meals = last_record.meals # It's already a JSON string
        finally:
            db.close()
            
        return render_template('add_food.html', preloaded_meals=preloaded_meals)
    
    if request.method == 'POST':
        data = request.json
        db = SessionLocal()
        try:
            from services import create_food_record
            create_food_record(db, current_user.id, data, 'web_pwa')
            return jsonify({"status": "success"})
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
        finally:
            db.close()

@app.route('/analyze_food', methods=['POST'])
@login_required
def analyze_food():
    if not gemini_api_key:
        return jsonify({"error": "Gemini API key not configured"}), 503
        
    try:
        data = request.json
        description = data.get('description')
        
        if not description:
            return jsonify({"error": "No description provided"}), 400
            
        model = genai.GenerativeModel('gemini-flash-latest', generation_config={"response_mime_type": "application/json"})
        prompt = f"""
        Analyze the following food description and estimate the macronutrients.
        Return a JSON object with the following keys: "protein" (int), "carbs" (int), "fat" (int), "calories" (int).
        
        Description: {description}
        """
        
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing food: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_exercise', methods=['POST'])
@login_required
def analyze_exercise():
    if not gemini_api_key:
        return jsonify({"error": "Gemini API key not configured"}), 503
        
    try:
        data = request.json
        description = data.get('description', '')
        image_b64 = data.get('image')
        mime_type = data.get('mime_type', 'image/jpeg')
        
        if not description and not image_b64:
            return jsonify({"error": "No description or image provided"}), 400
            
        model = genai.GenerativeModel('gemini-flash-latest', generation_config={"response_mime_type": "application/json"})
        
        prompt_text = """
        Analyze the following exercise description and/or image and extract the details.
        Return a JSON object with the following keys: 
        - "tipo_ejercicio" (str): Type of exercise (e.g., Running, Weightlifting)
        - "duracion_minutos" (int): Duration in minutes
        - "calorias_quemadas" (int): Estimated calories burned
        - "intensidad" (str): One of ["baja", "media", "alta"]
        - "otros_datos_de_interes" (str): Any other relevant info found
        
        Description: {description}
        """
        
        content = [prompt_text.format(description=description)]
        
        if image_b64:
            import base64
            image_bytes = base64.b64decode(image_b64)
            content.append({
                "mime_type": mime_type,
                "data": image_bytes
            })
        
        response = model.generate_content(content)
        result = json.loads(response.text)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error analyzing exercise: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/add/exercise', methods=['GET', 'POST'])
@login_required
def add_exercise():
    if request.method == 'GET':
        return render_template('add_exercise.html')
    
    if request.method == 'POST':
        data = request.json
        db = SessionLocal()
        try:
            from services import create_exercise_record
            
            record_data = {
                "date": data.get("date"),
                "exercise_type": data.get("tipo_ejercicio"),
                "duration_minutes": data.get("duracion_minutos"),
                "calories_burned": data.get("calorias_quemadas"),
                "intensity": data.get("intensidad"),
                "notes": data.get("otros_datos_de_interes"),
                "sync_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            create_exercise_record(db, current_user.id, record_data, 'web_pwa')
            return jsonify({"status": "success"})
        except Exception as e:
            db.rollback()
            return jsonify({"status": "error", "message": str(e)}), 400
        finally:
            db.close()

@app.route("/generate_plots")
@login_required
def generate_plots():
    user_id = current_user.id
    plots = {}
    
    try:
        with engine.connect() as conn:
            # 1. Weight Data
            weight_query = text("SELECT date, weight FROM weight_records WHERE user_id = :user_id ORDER BY date")
            weight_data = pd.read_sql_query(weight_query, conn, params={"user_id": user_id})
            
            if not weight_data.empty:
                weight_data['date'] = pd.to_datetime(weight_data['date'])
                weight_data['weight'] = pd.to_numeric(weight_data['weight'], errors='coerce')
                weight_data = weight_data.dropna(subset=['weight'])
                weight_data = weight_data[weight_data['weight'] > 0].sort_values('date')
                
                if not weight_data.empty:
                    weight_data['date_only'] = weight_data['date'].dt.date.astype(str)
                    daily_weight = weight_data.groupby('date_only', as_index=False).agg({'weight': 'last'})
                    
                    # Calculate range
                    min_w = daily_weight['weight'].min()
                    max_w = daily_weight['weight'].max()
                    padding = max(1.0, (max_w - min_w) * 0.1)
                    
                    fig_weight = px.bar(daily_weight, x='date_only', y='weight', title='Weight Over Time')
                    fig_weight.update_traces(
                        marker=dict(color='#4CAF50', line=dict(width=1, color='white'))
                    )
                    fig_weight.update_layout(
                        yaxis_title='Peso (kg)',
                        xaxis_title='Fecha',
                        yaxis=dict(range=[min_w - padding, max_w + padding]),
                        plot_bgcolor='white'
                    )
                    plots['weight'] = fig_weight.to_json()

            # 2. Blood Pressure Data
            bp_query = text("SELECT date, systolic as blood_pressure_sys, diastolic as blood_pressure_dia FROM blood_pressure_records WHERE user_id = :user_id ORDER BY date")
            bp_data = pd.read_sql_query(bp_query, conn, params={"user_id": user_id})
            
            if not bp_data.empty:
                bp_data['date'] = pd.to_datetime(bp_data['date'])
                bp_data['blood_pressure_sys'] = pd.to_numeric(bp_data['blood_pressure_sys'], errors='coerce')
                bp_data['blood_pressure_dia'] = pd.to_numeric(bp_data['blood_pressure_dia'], errors='coerce')
                bp_data = bp_data.dropna(subset=['blood_pressure_sys', 'blood_pressure_dia'])
                bp_data = bp_data[(bp_data['blood_pressure_sys'] > 0) & (bp_data['blood_pressure_dia'] > 0)].sort_values('date')

                if not bp_data.empty:
                    fig_bp = go.Figure()
                    fig_bp.add_trace(go.Scatter(x=bp_data["date"], y=bp_data["blood_pressure_sys"], name="Sistólica", mode='lines+markers'))
                    fig_bp.add_trace(go.Scatter(x=bp_data["date"], y=bp_data["blood_pressure_dia"], name="Diastólica", mode='lines+markers'))
                    fig_bp.update_layout(title="Blood Pressure Over Time", yaxis_title='Presión (mmHg)')
                    plots["blood_pressure"] = fig_bp.to_json()

            # 3. Glucose Data
            glucose_query = text("SELECT date, glucose_level FROM glucose_records WHERE user_id = :user_id ORDER BY date")
            glucose_data = pd.read_sql_query(glucose_query, conn, params={"user_id": user_id})
            
            if not glucose_data.empty:
                glucose_data['date'] = pd.to_datetime(glucose_data['date'])
                glucose_data['glucose_level'] = pd.to_numeric(glucose_data['glucose_level'], errors='coerce')
                glucose_data = glucose_data.dropna(subset=['glucose_level'])
                glucose_data = glucose_data[glucose_data['glucose_level'] > 0].sort_values('date')
                
                if not glucose_data.empty:
                    fig_glucose = px.line(glucose_data, x="date", y="glucose_level", title="Glucose Levels Over Time")
                    fig_glucose.update_traces(mode='lines+markers')
                    fig_glucose.update_layout(yaxis_title='Glucosa (mg/dL)')
                    plots["glucose"] = fig_glucose.to_json()

            # 4. Food Data
            food_query = text("SELECT date, meals FROM food_records WHERE user_id = :user_id ORDER BY date")
            food_data = pd.read_sql_query(food_query, conn, params={"user_id": user_id})
            
            if not food_data.empty:
                # Filter to keep only the last record per day
                food_data['date_obj'] = pd.to_datetime(food_data['date'])
                food_data['date_only'] = food_data['date_obj'].dt.date.astype(str)
                # Sort by date just in case, then group by date_only and take last
                food_data = food_data.sort_values('date').groupby('date_only').last().reset_index()

                meal_rows = []
                macro_rows = {}
                
                for idx, row in food_data.iterrows():
                    date_str = row['date_only']
                    meals_cell = row.get('meals')
                    
                    if not meals_cell:
                        continue
                        
                    try:
                        meals = json.loads(meals_cell) if isinstance(meals_cell, str) else meals_cell
                    except Exception:
                        continue
                        
                    if date_str not in macro_rows:
                        macro_rows[date_str] = {'date': date_str, 'protein': 0, 'carbs': 0, 'fat': 0}
                        
                    if isinstance(meals, dict):
                        for meal_name, meal_data in meals.items():
                            if isinstance(meal_data, dict):
                                p = float(meal_data.get('protein', 0) or 0)
                                c = float(meal_data.get('carbs', 0) or 0)
                                f = float(meal_data.get('fat', 0) or 0)
                                total_grams = p + c + f
                                
                                meal_rows.append({
                                    'date': date_str, 
                                    'meal': meal_name, 
                                    'grams': total_grams
                                })
                                
                                macro_rows[date_str]['protein'] += p
                                macro_rows[date_str]['carbs'] += c
                                macro_rows[date_str]['fat'] += f
                
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

        return jsonify(plots)

    except Exception as e:
        print(f"Error generating plots: {e}")
        return jsonify({"error": str(e)}), 500

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

@app.route("/analyze")
@login_required
def analyze_health_data():
    user_id = current_user.id
    try:
        stats = {
            "weight": {"mean": 0, "trend": "insufficient data"},
            "blood_pressure": {"sys_mean": 0, "dia_mean": 0},
            "glucose": {"mean": 0, "std": 0}
        }
        
        with engine.connect() as conn:
            # Weight Analysis
            w_query = text("SELECT weight FROM weight_records WHERE user_id = :user_id ORDER BY date")
            w_data = pd.read_sql_query(w_query, conn, params={"user_id": user_id})
            if not w_data.empty:
                w_data['weight'] = pd.to_numeric(w_data['weight'], errors='coerce')
                w_data = w_data[w_data['weight'] > 0]
                if not w_data.empty:
                    stats["weight"]["mean"] = w_data["weight"].mean()
                    if len(w_data) > 1:
                        stats["weight"]["trend"] = "increasing" if w_data["weight"].diff().mean() > 0 else "decreasing"

            # BP Analysis
            bp_query = text("SELECT systolic, diastolic FROM blood_pressure_records WHERE user_id = :user_id")
            bp_data = pd.read_sql_query(bp_query, conn, params={"user_id": user_id})
            if not bp_data.empty:
                bp_data['systolic'] = pd.to_numeric(bp_data['systolic'], errors='coerce')
                bp_data['diastolic'] = pd.to_numeric(bp_data['diastolic'], errors='coerce')
                bp_data = bp_data[(bp_data['systolic'] > 0) & (bp_data['diastolic'] > 0)]
                if not bp_data.empty:
                    stats["blood_pressure"]["sys_mean"] = bp_data["systolic"].mean()
                    stats["blood_pressure"]["dia_mean"] = bp_data["diastolic"].mean()

            # Glucose Analysis
            g_query = text("SELECT glucose_level FROM glucose_records WHERE user_id = :user_id")
            g_data = pd.read_sql_query(g_query, conn, params={"user_id": user_id})
            if not g_data.empty:
                g_data['glucose_level'] = pd.to_numeric(g_data['glucose_level'], errors='coerce')
                g_data = g_data[g_data['glucose_level'] > 0]
                if not g_data.empty:
                    stats["glucose"]["mean"] = g_data["glucose_level"].mean()
                    stats["glucose"]["std"] = g_data["glucose_level"].std() if len(g_data) > 1 else 0

        analysis = f"""
        Análisis básico de salud:
        - Peso promedio: {stats['weight']['mean']:.1f}kg (Tendencia: {stats['weight']['trend']})
        - Presión arterial promedio: {stats['blood_pressure']['sys_mean']:.0f}/{stats['blood_pressure']['dia_mean']:.0f}
        - Glucosa promedio: {stats['glucose']['mean']:.1f} (Desviación estándar: {stats['glucose']['std']:.1f})
        """
        
        analysis_result = {
            "statistics": stats,
            "analysis": analysis
        }
        
        # AI Analysis if enabled
        if gemini_api_key:
            try:
                analysis_prompt = f"""
                Analiza las siguientes metricas de salud:
                Peso: Media {stats['weight']['mean']:.1f}kg, Tendencia: {stats['weight']['trend']}
                Presión arterial: Media {stats['blood_pressure']['sys_mean']:.0f}/{stats['blood_pressure']['dia_mean']:.0f}
                Glucosa: Media {stats['glucose']['mean']:.1f}, Desviación estándar {stats['glucose']['std']:.1f}
                
                Provee un breve análisis de salud y recomendaciones.
                No presentes cuadros o tablas, realiza el análisis en un solo párrafo.
                """
                
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content(analysis_prompt)
                analysis_result['ai_analysis'] = response.text
            except Exception as e:
                analysis_result['ai_analysis'] = f"Análisis AI no disponible: {str(e)}"
        
        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_report(data):
    """Guarda el reporte localmente ya que WhatsApp no está configurado"""
    return save_local_report(data)

@app.route('/health_data', methods=['GET'])
@login_required
def get_health_data():
    try:
        user_id = current_user.id
        all_data = []
        
        with engine.connect() as conn:
            # 1. Weight
            w_query = text("SELECT date, weight FROM weight_records WHERE user_id = :user_id")
            w_rows = conn.execute(w_query, {"user_id": user_id}).fetchall()
            for row in w_rows:
                all_data.append({
                    "date": row.date,
                    "weight": row.weight,
                    "blood_pressure_sys": None,
                    "blood_pressure_dia": None,
                    "glucose_level": None,
                    "meals": None
                })
                
            # 2. BP
            bp_query = text("SELECT date, systolic, diastolic FROM blood_pressure_records WHERE user_id = :user_id")
            bp_rows = conn.execute(bp_query, {"user_id": user_id}).fetchall()
            for row in bp_rows:
                all_data.append({
                    "date": row.date,
                    "weight": None,
                    "blood_pressure_sys": row.systolic,
                    "blood_pressure_dia": row.diastolic,
                    "glucose_level": None,
                    "meals": None
                })
                
            # 3. Glucose
            g_query = text("SELECT date, glucose_level FROM glucose_records WHERE user_id = :user_id")
            g_rows = conn.execute(g_query, {"user_id": user_id}).fetchall()
            for row in g_rows:
                all_data.append({
                    "date": row.date,
                    "weight": None,
                    "blood_pressure_sys": None,
                    "blood_pressure_dia": None,
                    "glucose_level": row.glucose_level,
                    "meals": None
                })
                
            # 4. Food
            f_query = text("SELECT date, meals FROM food_records WHERE user_id = :user_id")
            f_rows = conn.execute(f_query, {"user_id": user_id}).fetchall()
            for row in f_rows:
                meals_parsed = None
                try:
                    if row.meals:
                        meals_parsed = json.loads(row.meals) if isinstance(row.meals, str) else row.meals
                except:
                    pass
                    
                all_data.append({
                    "date": row.date,
                    "weight": None,
                    "blood_pressure_sys": None,
                    "blood_pressure_dia": None,
                    "glucose_level": None,
                    "meals": meals_parsed
                })

        # Sort by date
        all_data.sort(key=lambda x: x['date'] if x['date'] else '')
        
        return jsonify({
            'status': 'success',
            'data': all_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)