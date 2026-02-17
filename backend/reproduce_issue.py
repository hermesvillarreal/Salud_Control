from sqlmodel import Session, create_engine, select
from app.models import FoodRecord, User, MealType
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql://salud_user:salud_password@db:5432/salud_control"
engine = create_engine(DATABASE_URL, echo=True)

def test_insertion():
    try:
        with Session(engine) as session:
            # Get a user (assuming user 1 exists)
            user = session.exec(select(User).where(User.id == 1)).first()
            if not user:
                print("User 1 not found. Creating test user.")
                user = User(username="test", email="test@test.com", password_hash="hash")
                session.add(user)
                session.commit()
                session.refresh(user)

            # Try to insert a record with 'desayuno'
            print("Attempting to insert 'desayuno'...")
            import traceback
            try:
                record = FoodRecord(
                    user_id=user.id,
                    fecha_hora=datetime.now(),
                    meal_type="desayuno", # Passing string, should be converted to Enum
                    description="Test Breakfast",
                    calories=100
                )
                print(f"Record created in memory: {record}")
                session.add(record)
                session.commit()
                print("Success!")
            except Exception as e:
                print("caught exception!")
                traceback.print_exc()
    except Exception as e:
        print(f"Outer Error: {e}")

if __name__ == "__main__":
    test_insertion()
