"""
Auto-migration script - runs without user confirmation
"""

import json
from datetime import datetime
from database import SessionLocal, engine
from models import Base, WeightRecord, BloodPressureRecord, GlucoseRecord, FoodRecord, HealthRecord
from sqlalchemy import text

print("="*50)
print("HEALTH RECORDS MIGRATION SCRIPT")
print("="*50)

# Create new tables
print("Creating new tables...")
Base.metadata.create_all(bind=engine)
print("✓ New tables created successfully")

db = SessionLocal()

try:
    # Get all health records
    print("\nFetching existing health_records...")
    health_records = db.query(HealthRecord).all()
    print(f"✓ Found {len(health_records)} health records to migrate")
    
    # Counters for migration stats
    weight_count = 0
    bp_count = 0
    glucose_count = 0
    food_count = 0
    
    # Migrate each record
    for record in health_records:
        # Migrate weight data
        if record.weight is not None and record.weight > 0:
            weight_record = WeightRecord(
                user_id=record.user_id,
                date=record.date,
                weight=record.weight,
                notes=record.notes or "",
                source=record.source or "migrated",
                sync_date=record.sync_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(weight_record)
            weight_count += 1
       
        # Migrate blood pressure data
        if (record.blood_pressure_sys is not None and record.blood_pressure_sys > 0) or \
           (record.blood_pressure_dia is not None and record.blood_pressure_dia > 0):
            bp_record = BloodPressureRecord(
                user_id=record.user_id,
                date=record.date,
                systolic=record.blood_pressure_sys or 0,
                diastolic=record.blood_pressure_dia or 0,
                notes=record.notes or "",
                source=record.source or "migrated",
                sync_date=record.sync_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(bp_record)
            bp_count += 1
        
        # Migrate glucose data
        if record.glucose_level is not None and record.glucose_level > 0:
            glucose_record = GlucoseRecord(
                user_id=record.user_id,
                date=record.date,
                glucose_level=record.glucose_level,
                notes=record.notes or "",
                source=record.source or "migrated",
                sync_date=record.sync_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(glucose_record)
            glucose_count += 1
        
        # Migrate food data
        if record.meals is not None and record.meals.strip():
            food_record = FoodRecord(
                user_id=record.user_id,
                date=record.date,
                meals=record.meals,
                notes=record.notes or "",
                source=record.source or "migrated",
                sync_date=record.sync_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            db.add(food_record)
            food_count += 1
    
    # Commit all changes
    print("\nCommitting migrated data...")
    db.commit()
    
    # Print migration summary
    print("\n" + "="*50)
    print("MIGRATION SUMMARY")
    print("="*50)
    print(f"Total health_records processed: {len(health_records)}")
    print(f"Weight records created: {weight_count}")
    print(f"Blood pressure records created: {bp_count}")
    print(f"Glucose records created: {glucose_count}")
    print(f"Food records created: {food_count}")
    print("="*50)
    print("\n✓ Migration completed successfully!")
    print("\nNote: Original health_records table has been kept as backup.")
    
except Exception as e:
    print(f"\n✗ Error during migration: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    raise
finally:
    db.close()
