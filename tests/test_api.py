"""
Cardora API Testing Script
Run this to test authentication and endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_json(data):
    """Pretty print JSON"""
    print(json.dumps(data, indent=2))

def test_api():
    print("=" * 60)
    print("CARDORA API TESTING")
    print("=" * 60)

    # Step 1: Register
    print("\n=== STEP 1: Register a new user ===")
    register_data = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("[OK] User registered successfully!")
            print_json(response.json())
        elif response.status_code == 400:
            print("[WARN] User already exists, proceeding to login...")
        else:
            print(f"[ERROR] Registration failed: {response.status_code}")
            print_json(response.json())
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return

    # Step 2: Login
    print("\n=== STEP 2: Login and get token ===")
    login_data = {
        "email": "test@example.com",
        "password": "Test123!"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            print("[OK] Login successful!")
            print(f"Token: {token[:50]}...")
        else:
            print(f"[ERROR] Login failed: {response.status_code}")
            print_json(response.json())
            return
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return

    # Create auth header
    headers = {"Authorization": f"Bearer {token}"}

    # Step 3: Get user profile
    print("\n=== STEP 3: Get user profile (authenticated) ===")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            print("[OK] Successfully retrieved user profile!")
            print_json(response.json())
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            print_json(response.json())
    except Exception as e:
        print(f"[ERROR] Error: {e}")

    # Step 4: Get categories
    print("\n=== STEP 4: Get categories (authenticated) ===")
    try:
        response = requests.get(f"{BASE_URL}/categories", headers=headers)
        if response.status_code == 200:
            print("[OK] Successfully retrieved categories!")
            categories = response.json()
            print(f"Found {len(categories)} categories:")
            print_json(categories)
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            print_json(response.json())
    except Exception as e:
        print(f"[ERROR] Error: {e}")

    # Step 5: Get credit cards
    print("\n=== STEP 5: Get credit cards (authenticated) ===")
    try:
        response = requests.get(f"{BASE_URL}/credit-cards", headers=headers)
        if response.status_code == 200:
            print("[OK] Successfully retrieved credit cards!")
            cards = response.json()
            print(f"Found {len(cards)} cards:")
            print_json(cards)
        else:
            print(f"[ERROR] Failed: {response.status_code}")
            print_json(response.json())
    except Exception as e:
        print(f"[ERROR] Error: {e}")

    # Save token for future use
    print("\n" + "=" * 60)
    print("TESTING COMPLETE!")
    print("=" * 60)
    print("\nTo use this token in curl commands:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/categories')
    print("\nOr in Swagger UI:")
    print("1. Go to http://localhost:8000/docs")
    print("2. Click 'Authorize' button")
    print(f"3. Paste this token: {token}")
    print("4. Click 'Authorize' and 'Close'")
    print("5. Now you can test all endpoints!")

if __name__ == "__main__":
    test_api()
