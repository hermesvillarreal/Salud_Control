import json
from datetime import datetime
from models import User, HealthRecord
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

def create_health_record(db: Session, user_id: int, record_data: dict, source: str) -> HealthRecord:
    """Create and save a new health record."""
    # Normalize meals field
    meals = record_data.get('meals') or record_data.get('meals_data') or record_data.get('meals_data_json')
    try:
        meals_json = json.dumps(meals) if meals is not None else None
    except Exception:
        # If meals already a JSON string, keep as is
        meals_json = meals if isinstance(meals, str) else None

    # Use provided sync_date or current time
    sync_date = record_data.get('sync_date') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    new_record = HealthRecord(
        user_id=user_id,
        date=record_data.get("date"),
        weight=record_data.get("weight"),
        blood_pressure_sys=record_data.get("blood_pressure_sys"),
        blood_pressure_dia=record_data.get("blood_pressure_dia"),
        glucose_level=record_data.get("glucose_level"),
        meals=meals_json,
        notes=record_data.get("notes", ""),
        source=source,
        sync_date=sync_date
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record
