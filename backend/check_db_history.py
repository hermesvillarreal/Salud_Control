import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import engine
from app.models import CalculatorResult
from sqlmodel import Session, select

def check_history():
    print("Checking CalculatorResult records in database...")
    with Session(engine) as session:
        records = session.exec(select(CalculatorResult)).all()
        print(f"Total records found: {len(records)}")
        for i, record in enumerate(records):
            print(f"Record {i+1}: ID={record.id}, UserID={record.user_id}, Type={record.calculator_type}, Time={record.fecha_hora}")
            try:
                inputs = json.loads(record.input_data)
                results = json.loads(record.result_data)
                print(f"  Inputs: {list(inputs.keys())}")
                print(f"  Results: {list(results.keys())}")
            except Exception as e:
                print(f"  Error parsing JSON: {e}")
            print("-" * 20)

if __name__ == "__main__":
    check_history()
