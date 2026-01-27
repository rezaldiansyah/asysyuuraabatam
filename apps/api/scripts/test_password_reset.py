import requests
import re
import time

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/auth/login"
FORGOT_URL = f"{API_URL}/auth/forgot-password"
RESET_URL = f"{API_URL}/auth/reset-password"

EMAIL = "admin@asysyuura.sch.id"
NEW_PASSWORD = "newpassword123"

def test_password_reset():
    # 1. Request Password Reset
    print(f"1. Requesting password reset for {EMAIL}...")
    res = requests.post(FORGOT_URL, json={"email": EMAIL})
    if res.status_code == 200:
        print("   Success: Request sent.")
    else:
        print(f"   Fail: {res.status_code} {res.text}")
        return

    time.sleep(1) # Wait for log flush

    # 2. Get Token from log
    print("2. Reading token from api.log...")
    try:
        with open("api.log", "r") as f:
            log_content = f.read()
            # Find the LAST occurrence of the token log
            matches = list(re.finditer(r"token=([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+)", log_content))
            if matches:
                token = matches[-1].group(1) # Get the last one
                print(f"   Success: Found token {token[:10]}...")
            else:
                print("   Fail: Token not found in log. Log tail:")
                print(log_content[-1000:] if len(log_content) > 1000 else log_content)
                return
    except FileNotFoundError:
        print("   Fail: api.log not found")
        return

    # 3. Reset Password
    print("3. Resetting password...")
    res = requests.post(RESET_URL, json={"token": token, "new_password": NEW_PASSWORD})
    if res.status_code == 200:
        print("   Success: Password reset.")
    else:
        print(f"   Fail: {res.status_code} {res.text}")
        return

    # 4. Login with New Password
    print("4. Logging in with new password...")
    res = requests.post(LOGIN_URL, data={"username": EMAIL, "password": NEW_PASSWORD})
    if res.status_code == 200:
        print("   PASS: Implementation verified.")
    else:
        print(f"   FAIL: Login failed {res.status_code} {res.text}")

if __name__ == "__main__":
    test_password_reset()
