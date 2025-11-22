import json
from datetime import datetime
from models import User, HealthRecord, WeightRecord, BloodPressureRecord, GlucoseRecord, FoodRecord, ExerciseRecord
from sqlalchemy.orm import Session

def get_or_create_user(db: Session, email: str, name: str, phone: str = None) -> User:
    """Get an existing user by email or create a new one."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(name=name, email=email, phone=phone)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def create_weight_record(db: Session, user_id: int, record_data: dict, source: str) -> WeightRecord:
    """Create and save a new weight record."""
    sync_date = record_data.get('sync_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_record = WeightRecord(
        user_id=user_id,
        date=record_data.get("date"),
        weight=record_data.get("weight"),
        notes=record_data.get("notes", ""),
        source=source,
        sync_date=sync_date
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def create_blood_pressure_record(db: Session, user_id: int, record_data: dict, source: str) -> BloodPressureRecord:
    """Create and save a new blood pressure record."""
    sync_date = record_data.get('sync_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_record = BloodPressureRecord(
        user_id=user_id,
        date=record_data.get("date"),
        systolic=record_data.get("blood_pressure_sys"),
        diastolic=record_data.get("blood_pressure_dia"),
        notes=record_data.get("notes", ""),
        source=source,
        sync_date=sync_date
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def create_glucose_record(db: Session, user_id: int, record_data: dict, source: str) -> GlucoseRecord:
    """Create and save a new glucose record."""
    sync_date = record_data.get('sync_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_record = GlucoseRecord(
        user_id=user_id,
        date=record_data.get("date"),
        glucose_level=record_data.get("glucose_level"),
        notes=record_data.get("notes", ""),
        source=source,
        sync_date=sync_date
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def create_food_record(db: Session, user_id: int, record_data: dict, source: str) -> FoodRecord:
    """Create and save a new food record."""
    sync_date = record_data.get('sync_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Normalize meals field
    meals = record_data.get('meals') or record_data.get('meals_data') or record_data.get('meals_data_json')
    try:
        meals_json = json.dumps(meals) if meals is not None else None
    except Exception:
        # If meals already a JSON string, keep as is
        meals_json = meals if isinstance(meals, str) else None
    
    new_record = FoodRecord(
        user_id=user_id,
        date=record_data.get("date"),
        meals=meals_json,
        notes=record_data.get("notes", ""),
        source=source,
        sync_date=sync_date
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def create_exercise_record(db: Session, user_id: int, record_data: dict, source: str) -> ExerciseRecord:
    """Create and save a new exercise record."""
    sync_date = record_data.get('sync_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_record = ExerciseRecord(
        user_id=user_id,
        date=record_data.get("date"),
        exercise_type=record_data.get("exercise_type"),
        duration_minutes=record_data.get("duration_minutes"),
        calories_burned=record_data.get("calories_burned"),
        intensity=record_data.get("intensity"),
        notes=record_data.get("notes", ""),
        source=source,
        sync_date=sync_date
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def create_health_record(db: Session, user_id: int, record_data: dict, source: str):
    """
    Create health record(s) based on the data provided.
    This function intelligently detects which types of data are present and creates the appropriate records.
    Maintains backward compatibility with old code.
    """
    created_records = []
    
    # Check and create weight record if weight data is present
    if record_data.get("weight") is not None and record_data.get("weight") != 0:
        weight_record = create_weight_record(db, user_id, record_data, source)
        created_records.append(("weight", weight_record))
    
    # Check and create blood pressure record if pressure data is present
    if (record_data.get("blood_pressure_sys") is not None and record_data.get("blood_pressure_sys") != 0) or \
       (record_data.get("blood_pressure_dia") is not None and record_data.get("blood_pressure_dia") != 0):
        bp_record = create_blood_pressure_record(db, user_id, record_data, source)
        created_records.append(("blood_pressure", bp_record))
    
    # Check and create glucose record if glucose data is present
    if record_data.get("glucose_level") is not None and record_data.get("glucose_level") != 0:
        glucose_record = create_glucose_record(db, user_id, record_data, source)
        created_records.append(("glucose", glucose_record))
    
    # Check and create food record if meals data is present
    meals = record_data.get('meals') or record_data.get('meals_data') or record_data.get('meals_data_json')
    if meals is not None:
        food_record = create_food_record(db, user_id, record_data, source)
        created_records.append(("food", food_record))

    # Check and create exercise record if exercise data is present
    if record_data.get("exercise_type") is not None:
        exercise_record = create_exercise_record(db, user_id, record_data, source)
        created_records.append(("exercise", exercise_record))
    
    # Return the first record for backward compatibility, or all records info
    if created_records:
        return created_records[0][1]  # Return first record for backward compatibility
    
    return None
