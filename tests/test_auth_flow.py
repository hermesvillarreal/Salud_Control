import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_auth_flow():
    session = requests.Session()
    
    # 1. Try to access protected route (should fail or redirect)
    print("Testing access to protected route without login...")
    response = session.get(f"{BASE_URL}/")
    if response.url.endswith("/login?next=%2F"):
        print("SUCCESS: Redirected to login page.")
    elif response.status_code == 401:
         print("SUCCESS: Access denied (401).")
    else:
        # It might redirect to /login
        if "/login" in response.url:
             print("SUCCESS: Redirected to login.")
        else:
            print(f"FAILURE: Accessed protected route? Status: {response.status_code}, URL: {response.url}")

    # 2. Register a new user
    email = "testuser@example.com"
    password = "password123"
    print(f"\nRegistering user {email}...")
    response = session.post(f"{BASE_URL}/register", data={
        "name": "Test User",
        "email": email,
        "password": password,
        "phone": "1234567890"
    })
    
    if response.status_code == 200 and "Panel de Control" in response.text: # Assuming redirect to index
        print("SUCCESS: Registration successful and redirected to index.")
    elif response.status_code == 200 and "Iniciar Sesión" in response.text: # Maybe redirects to login?
         print("SUCCESS: Registration successful (redirected to login).")
    else:
        # If user already exists, it might redirect to register with flash message
        if "El correo ya está registrado" in response.text:
            print("NOTE: User already exists, proceeding to login.")
        else:
            print(f"Registration response: {response.status_code}")

    # 3. Login
    print(f"\nLogging in as {email}...")
    response = session.post(f"{BASE_URL}/login", data={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200 and "Panel de Control" in response.text:
        print("SUCCESS: Login successful.")
    else:
        print(f"FAILURE: Login failed. Status: {response.status_code}")
        # print(response.text)
        return

    # 4. Access protected route again
    print("\nAccessing protected route after login...")
    response = session.get(f"{BASE_URL}/")
    if response.status_code == 200 and "Panel de Control" in response.text:
        print("SUCCESS: Accessed index page.")
    else:
        print(f"FAILURE: Could not access index page. Status: {response.status_code}")

    # 5. Add a record
    print("\nAdding a health record...")
    record_data = {
        "date": "2023-10-27 10:00:00",
        "weight": 75.5,
        "blood_pressure_sys": 120,
        "blood_pressure_dia": 80,
        "glucose_level": 90,
        "meals": "{}",
        "notes": "Test record"
    }
    response = session.post(f"{BASE_URL}/add_record", json=record_data)
    if response.status_code == 200:
        print("SUCCESS: Record added.")
    else:
        print(f"FAILURE: Could not add record. Status: {response.status_code}")
        print(response.text)

    # 6. Verify data isolation (check if we can see the record)
    print("\nVerifying data visibility...")
    response = session.get(f"{BASE_URL}/health_data")
    data = response.json()
    if data['status'] == 'success':
        records = data['data']
        found = any(r['weight'] == 75.5 for r in records)
        if found:
            print("SUCCESS: Record found in user data.")
        else:
            print("FAILURE: Record NOT found in user data.")
    else:
        print("FAILURE: Could not fetch health data.")

    # 7. Logout
    print("\nLogging out...")
    response = session.get(f"{BASE_URL}/logout")
    if "/login" in response.url:
        print("SUCCESS: Logged out.")
    else:
        print("FAILURE: Logout might have failed.")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Is it running?")
