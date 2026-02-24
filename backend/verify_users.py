
import sys
import os
from sqlmodel import Session, select
from dotenv import load_dotenv

# Add current directory to path so we can import 'app'
# Assuming we run this from the root or backend dir
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env vars from root .env if it exists
load_dotenv('.env')

from app.database import engine
from app.models import User

def list_users():
    print("Listing users in database...")
    try:
        with Session(engine) as session:
            statement = select(User)
            users = session.exec(statement).all()
            print(f"Total users found: {len(users)}")
            for user in users:
                print(f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Hash: {user.password_hash[:10]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_users()
