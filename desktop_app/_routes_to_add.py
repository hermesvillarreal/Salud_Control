# Add these routes after the /add_record route in app.py

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
