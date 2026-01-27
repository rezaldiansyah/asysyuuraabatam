import sys
import os
from sqlalchemy.orm import Session

# Add apps/api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from database import SessionLocal
import models
import auth

def debug_login():
    db = SessionLocal()
    try:
        print("--- Debugging Login ---")
        
        # 1. Check User Existence
        username_nik = "999999"
        username_email = "admin@asysyuura.sch.id"
        
        user_nik = db.query(models.User).filter(models.User.nik == username_nik).first()
        user_email = db.query(models.User).filter(models.User.email == username_email).first()
        
        if not user_nik and not user_email:
            print("CRITICAL: Admin user NOT FOUND in database.")
            return

        user = user_nik or user_email
        print(f"User Found: ID={user.id}, NIK={user.nik}, Email={user.email}, Name={user.full_name}")
        
        # 2. Check Password
        passwords_to_try = ["admin123", "password"]
        success = False
        
        for pwd in passwords_to_try:
            is_valid = auth.verify_password(pwd, user.password_hash)
            print(f"Testing password '{pwd}': {'MATCH' if is_valid else 'FAIL'}")
            if is_valid:
                success = True
                print(f"SUCCESS! The correct password is: {pwd}")
                break
        
        if not success:
            print("CRITICAL: User exists but neither 'admin123' nor 'password' matches the hash.")
            print("Resetting password to 'admin123'...")
            
            # 3. Emergency Reset
            new_hash = auth.get_password_hash("admin123")
            user.password_hash = new_hash
            db.commit()
            print("Password has been reset to: admin123")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_login()
