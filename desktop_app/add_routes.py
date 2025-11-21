#!/usr/bin/env python
# Script to add individual routes to app.py

routes_to_add = '''
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
        return render_template('add_food.html')
    
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

'''

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the location to insert (after /add_record route)
# Look for the pattern: "db.close()\n\n\n@app.route(\"/generate_plots\")"
import re

pattern = r'(db\.close\(\)\s*\n\s*\n\s*@app\.route\("/generate_plots"\))'
match = re.search(pattern, content)

if match:
    # Insert routes before @app.route("/generate_plots")
    insert_pos = match.start(1)
    new_content = content[:insert_pos] + 'db.close()\n' + routes_to_add + '\n@app.route("/generate_plots")' + content[match.end(1):]
    
    # Write back to file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Routes added successfully!")
    print("Added routes: /add/weight, /add/pressure, /add/glucose, /add/food")
else:
    print("✗ Could not find insertion point")
    print("Pattern not found in file")
