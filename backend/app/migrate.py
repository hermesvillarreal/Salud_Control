from sqlalchemy import text
from app.database import engine

def migrate():
    columns_to_add = [
        ("age", "INTEGER"),
        ("gender", "VARCHAR(255)"),
        ("height_cm", "FLOAT"),
        ("weight_kg", "FLOAT"),
        ("activity_level", "VARCHAR(255)")
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                print(f"Adding column {col_name} to table 'user'...")
                conn.execute(text(f'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS {col_name} {col_type}'))
                conn.commit()
                print(f"Column {col_name} added or already exists.")
            except Exception as e:
                print(f"Error adding column {col_name}: {e}")

    # Add columns for appointment table
    appointment_columns = [
        ("location", "VARCHAR(255)"),
        ("phone_number", "VARCHAR(255)")
    ]
    with engine.connect() as conn:
        for col_name, col_type in appointment_columns:
            try:
                print(f"Adding column {col_name} to table 'appointment'...")
                conn.execute(text(f'ALTER TABLE appointment ADD COLUMN IF NOT EXISTS {col_name} {col_type}'))
                conn.commit()
                print(f"Column {col_name} added or already exists.")
            except Exception as e:
                print(f"Error adding column {col_name} to appointment: {e}")

if __name__ == "__main__":
    migrate()
