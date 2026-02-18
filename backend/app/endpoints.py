from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
import shutil
import os
import json
from datetime import datetime

from app.database import get_session
from app.models import (
    User, UserCreate, WeightRecord, BloodPressureRecord, GlucoseRecord, 
    FoodRecord, ExerciseRecord, ClinicalDocument, UserRole, MealType,
    CalculatorResult, WaistHipRecord
)
from app.auth.hash_utils import get_password_hash, verify_password
from app.auth.jwt_utils import create_access_token
from app.auth.dependencies import get_current_user
from app.services.ai_service import (
    analyze_food_text, analyze_food_image, analyze_health_summary,
    analyze_exercise_text, analyze_exercise_image
)
from app.services import calculator_service

router = APIRouter()

# --- AUTH ENDPOINTS ---

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Check if user exists (username or email)
    existing_user = session.exec(
        select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User created successfully"}

@router.post("/auth/login")
def login(user_data: dict, session: Session = Depends(get_session)):
    login_id = user_data.get("username") # Frontend sends login_id as 'username'
    password = user_data.get("password")
    
    if not login_id or not password:
        raise HTTPException(status_code=400, detail="Username/Email and password required")

    # Search by username OR email
    user = session.exec(
        select(User).where((User.username == login_id) | (User.email == login_id))
    ).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "name": user.full_name or user.username,
            "is_telegram_linked": user.telegram_chat_id is not None
        }
    }

@router.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "name": user.full_name or user.username,
        "is_telegram_linked": user.telegram_chat_id is not None,
        "daily_calories_goal": user.daily_calories_goal,
        "daily_protein_goal": user.daily_protein_goal,
        "daily_carbs_goal": user.daily_carbs_goal,
        "daily_fat_goal": user.daily_fat_goal,
        "current_goal": user.current_goal
    }

@router.post("/auth/telegram-unlink")
def unlink_telegram(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    user.telegram_chat_id = None
    session.add(user)
    session.commit()
    return {"message": "Telegram account unlinked successfully"}

@router.get("/auth/telegram-token")
def get_telegram_token(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    import secrets
    token = secrets.token_urlsafe(16)
    user.telegram_auth_token = token
    session.add(user)
    session.commit()
    return {"token": token}

@router.patch("/auth/me")
def update_user_profile(
    user_data: dict,
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Update user profile, including nutritional goals"""
    # Allowed fields to update
    allowed_fields = [
        "full_name", 
        "daily_calories_goal", "daily_protein_goal", 
        "daily_carbs_goal", "daily_fat_goal",
        "current_goal",
        "age", "gender", "height_cm", "weight_kg", "activity_level"
    ]
    
    for key, value in user_data.items():
        if key in allowed_fields:
            setattr(user, key, value)
            
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "name": user.full_name or user.username,
        "is_telegram_linked": user.telegram_chat_id is not None,
        "daily_calories_goal": user.daily_calories_goal,
        "daily_protein_goal": user.daily_protein_goal,
        "daily_carbs_goal": user.daily_carbs_goal,
        "daily_fat_goal": user.daily_fat_goal,
        "current_goal": user.current_goal
    }

# --- HEALTH METRICS CRUD ---

# Helper mapping for generic CRUD to avoid code repetition in this implementation
METRIC_MODELS = {
    "weight": WeightRecord,
    "bp": BloodPressureRecord,
    "glucose": GlucoseRecord,
    "waist_hip": WaistHipRecord
}

@router.post("/health/{metric_type}")
def create_health_record(
    metric_type: str, 
    data: dict, 
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    model_class = METRIC_MODELS.get(metric_type)
    if not model_class:
        raise HTTPException(status_code=404, detail="Metric type not found")
    
    record = model_class(**data, user_id=user.id)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@router.get("/health/{metric_type}", response_model=List)
def get_health_records(
    metric_type: str, 
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    model_class = METRIC_MODELS.get(metric_type)
    if not model_class:
        raise HTTPException(status_code=404, detail="Metric type not found")
    
    records = session.exec(select(model_class).where(model_class.user_id == user.id)).all()
    return records

# --- FOOD & EXERCISE ---

@router.post("/food/analyze")
async def analyze_food(description: str, user: User = Depends(get_current_user)):
    macros = await analyze_food_text(description)
    return macros

@router.post("/food/analyze-image")
async def analyze_food_img(
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    image_bytes = await file.read()
    print(f"DEBUG: Processing image analysis for user {user.id}")
    macros = await analyze_food_image(image_bytes, file.content_type, description or "")
    if "error" in macros:
        print(f"DEBUG: Error in analysis: {macros['error']}")
    return macros

@router.post("/food/log")
def log_food(
    data: dict, 
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    if 'meal_type' in data and isinstance(data['meal_type'], str):
        data['meal_type'] = data['meal_type'].lower()
    record = FoodRecord(**data, user_id=user.id)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@router.get("/food", response_model=List[FoodRecord])
def get_food_logs(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(FoodRecord).where(FoodRecord.user_id == user.id).order_by(FoodRecord.fecha_hora.desc())).all()

@router.put("/food/{id}", response_model=FoodRecord)
def update_food_log(
    id: int,
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    record = session.get(FoodRecord, id)
    if not record:
        raise HTTPException(status_code=404, detail="Food record not found")
    if record.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this record")
    
    for key, value in data.items():
        if key != "id" and key != "user_id": # Prevent changing ID or ownership
             setattr(record, key, value)

    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@router.post("/exercise")
def log_exercise(
    data: dict, 
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    record = ExerciseRecord(**data, user_id=user.id)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.post("/exercise/analyze")
async def analyze_exercise(description: str, user: User = Depends(get_current_user)):
    exercise_data = await analyze_exercise_text(description)
    return exercise_data

@router.post("/exercise/analyze-image")
async def analyze_exercise_img(
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    image_bytes = await file.read()
    exercise_data = await analyze_exercise_image(image_bytes, file.content_type, description or "")
    return exercise_data

@router.get("/exercise", response_model=List[ExerciseRecord])
def get_exercise_logs(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(ExerciseRecord).where(ExerciseRecord.user_id == user.id).order_by(ExerciseRecord.fecha_hora.desc())).all()

@router.put("/exercise/{id}", response_model=ExerciseRecord)
def update_exercise_log(
    id: int,
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    record = session.get(ExerciseRecord, id)
    if not record:
        raise HTTPException(status_code=404, detail="Exercise record not found")
    if record.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this record")
    
    for key, value in data.items():
        if key != "id" and key != "user_id": # Prevent changing ID or ownership
             setattr(record, key, value)

    session.add(record)
    session.commit()
    session.refresh(record)
    return record

# --- CLINICAL DOCUMENTS ---

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/documents/upload")
async def upload_document(
    title: str = Form(...),
    doc_type: str = Form(...),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    file_path = os.path.join(UPLOAD_DIR, f"{user.id}_{datetime.now().timestamp()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    doc = ClinicalDocument(
        user_id=user.id,
        title=title,
        document_type=doc_type,
        file_path=file_path,
        notes=notes,
        fecha_hora=datetime.now()
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc

@router.get("/documents", response_model=List[ClinicalDocument])
def get_documents(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(ClinicalDocument).where(ClinicalDocument.user_id == user.id)).all()

# --- DASHBOARD/ANALYSIS ---

@router.get("/analysis/summary")
async def get_health_analysis(
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Fetch recent history
    weights = session.exec(select(WeightRecord).where(WeightRecord.user_id == user.id).limit(5)).all()
    bp = session.exec(select(BloodPressureRecord).where(BloodPressureRecord.user_id == user.id).limit(5)).all()
    glucose = session.exec(select(GlucoseRecord).where(GlucoseRecord.user_id == user.id).limit(5)).all()
    
    user_history = {
        "user": user.full_name or user.username,
        "recent_weights": [w.weight for w in weights],
        "recent_blood_pressure": [{"sys": b.systolic, "dia": b.diastolic} for b in bp],
        "recent_glucose": [g.glucose_level for g in glucose]
    }
    
    ai_verdict = await analyze_health_summary(user_history)
    
    return {
        "stats": {
            "weight_count": len(weights),
            "bp_count": len(bp),
            "glucose_count": len(glucose)
        },
        "ai_summary": ai_verdict
    }

# --- HEALTH CALCULATORS ---

@router.post("/calculators/tdee")
def calculate_tdee_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate TDEE and save result"""
    result = calculator_service.calculate_tdee(
        age=data["age"],
        gender=data["gender"],
        weight_kg=data["weight_kg"],
        height_cm=data["height_cm"],
        activity_level=data["activity_level"]
    )
    
    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="tdee",
        fecha_hora=data.get("fecha_hora"),
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.post("/calculators/macro")
def calculate_macro_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate macros and save result"""
    result = calculator_service.calculate_macros(
        tdee=data["tdee"],
        goal=data["goal"],
        weight_kg=data["weight_kg"],
        protein_preference=data.get("protein_preference", "moderate")
    )
    
    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="macro",
        fecha_hora=data.get("fecha_hora"),
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.post("/calculators/bmi")
def calculate_bmi_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate BMI and save result"""
    result = calculator_service.calculate_bmi(
        weight_kg=data["weight_kg"],
        height_cm=data["height_cm"]
    )
    
    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="bmi",
        fecha_hora=data.get("fecha_hora"),
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.post("/calculators/ascvd")
def calculate_ascvd_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate ASCVD risk and save result"""
    result = calculator_service.calculate_ascvd_risk(
        age=data["age"],
        gender=data["gender"],
        race=data["race"],
        total_cholesterol=data["total_cholesterol"],
        hdl_cholesterol=data["hdl_cholesterol"],
        systolic_bp=data["systolic_bp"],
        is_diabetic=data["is_diabetic"],
        is_smoker=data["is_smoker"],
        on_bp_medication=data["on_bp_medication"]
    )
    
    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="ascvd",
        fecha_hora=data.get("fecha_hora"),
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.post("/calculators/rcc")
def calculate_rcc_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate RCC and save result to CalculatorResult"""
    result = calculator_service.calculate_rcc(
        waist_cm=data["waist_cm"],
        hip_cm=data["hip_cm"],
        gender=data.get("gender", user.gender or "male")
    )
    
    # Parse fecha_hora if it comes as a string
    fecha_hora = data.get("fecha_hora")
    if isinstance(fecha_hora, str):
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora)
        except ValueError:
            fecha_hora = datetime.now()
    elif not fecha_hora:
        fecha_hora = datetime.now()

    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="rcc",
        fecha_hora=fecha_hora,
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.post("/calculators/weights")
def calculate_weights_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate Weights expenditure and save result"""
    result = calculator_service.calculate_weights_expenditure(
        weight_kg=data["weight_kg"],
        time_min=data["time_min"],
        intensity=data.get("intensity")
    )
    
    # Parse fecha_hora if it comes as a string
    fecha_hora = data.get("fecha_hora")
    if isinstance(fecha_hora, str):
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora)
        except ValueError:
            fecha_hora = datetime.now()
    elif not fecha_hora:
        fecha_hora = datetime.now()

    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="weights",
        fecha_hora=fecha_hora,
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.post("/calculators/expenditure")
def calculate_expenditure_endpoint(
    data: dict,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Calculate Caloric Expenditure and save result"""
    result = calculator_service.calculate_caloric_expenditure(
        weight_kg=data["weight_kg"],
        duration_min=data["duration_min"],
        activity_met=data["activity_met"],
        rpe=data.get("rpe")
    )
    
    # Parse fecha_hora if it comes as a string
    fecha_hora = data.get("fecha_hora")
    if isinstance(fecha_hora, str):
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora)
        except ValueError:
            fecha_hora = datetime.now()
    elif not fecha_hora:
        fecha_hora = datetime.now()

    # Save to database
    calc_record = CalculatorResult(
        user_id=user.id,
        calculator_type="expenditure",
        fecha_hora=fecha_hora,
        input_data=json.dumps(data),
        result_data=json.dumps(result),
        notes=data.get("notes")
    )
    session.add(calc_record)
    session.commit()
    session.refresh(calc_record)
    
    return {"id": calc_record.id, "result": result}

@router.get("/calculators/history")
def get_calculator_history(
    calculator_type: Optional[str] = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get calculator history, optionally filtered by type"""
    query = select(CalculatorResult).where(CalculatorResult.user_id == user.id)
    
    if calculator_type:
        query = query.where(CalculatorResult.calculator_type == calculator_type)
    
    query = query.order_by(CalculatorResult.fecha_hora.desc())
    records = session.exec(query).all()
    
    # Parse JSON data for response
    history = []
    for record in records:
        history.append({
            "id": record.id,
            "calculator_type": record.calculator_type,
            "fecha_hora": record.fecha_hora.isoformat(),
            "input_data": json.loads(record.input_data),
            "result_data": json.loads(record.result_data),
            "notes": record.notes
        })
    
    return history

@router.get("/calculators/history/{id}")
def get_calculator_result(
    id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get specific calculator result"""
    record = session.get(CalculatorResult, id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Calculator result not found")
    
    if record.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this result")
    
    return {
        "id": record.id,
        "calculator_type": record.calculator_type,
        "fecha_hora": record.fecha_hora.isoformat(),
        "input_data": json.loads(record.input_data),
        "result_data": json.loads(record.result_data),
        "notes": record.notes
    }

