import sys
import os

# Add desktop_app to path
sys.path.append(os.path.join(os.getcwd(), 'desktop_app'))

from database import SessionLocal, engine
from models import User, HealthRecord
from sqlalchemy import text

def verify_db():
    print("Verifying database connection...")
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print(f"Connection successful: {result[0]}")
            
        # Test ORM
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            record_count = db.query(HealthRecord).count()
            print(f"Users in DB: {user_count}")
            print(f"Health Records in DB: {record_count}")
            
            if user_count > 0:
                user = db.query(User).first()
                print(f"First user: {user.name} ({user.email})")
                
        finally:
            db.close()
            
        print("Verification passed!")
        return True
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_db()
