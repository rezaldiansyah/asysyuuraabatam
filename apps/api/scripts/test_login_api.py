import requests
import sys

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/auth/login"

def test_login():
    try:
        print(f"Attempting login to {LOGIN_URL}...")
        response = requests.post(LOGIN_URL, data={
            "username": "999999",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            print("LOGIN SUCCESS!")
            print(f"Token: {response.json().get('access_token')[:20]}...")
        else:
            print(f"LOGIN FAILED. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
