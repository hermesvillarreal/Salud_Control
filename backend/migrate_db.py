from sqlmodel import create_engine, text
import os
from app.database import engine

def migrate():
    with engine.connect() as conn:
        print("Checking for tabla_nutricional column in foodrecord table...")
        try:
            # Check if column exists (Postgres)
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='foodrecord' AND column_name='tabla_nutricional';"))
            if not res.fetchone():
                print("Adding tabla_nutricional column...")
                conn.execute(text("ALTER TABLE foodrecord ADD COLUMN tabla_nutricional TEXT;"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column already exists.")
        except Exception as e:
            # Fallback for SQLite
            try:
                print(f"Postgres check failed ({e}), trying SQLite...")
                conn.execute(text("ALTER TABLE foodrecord ADD COLUMN tabla_nutricional TEXT;"))
                conn.commit()
                print("Column added successfully (SQLite).")
            except Exception as e2:
                print(f"Migration failed: {e2}")

if __name__ == "__main__":
    migrate()
