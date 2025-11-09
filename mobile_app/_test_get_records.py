from database import MobileDatabase
import json

def main():
    db = MobileDatabase()
    records = db.get_user_records(1)
    print(json.dumps(records, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
