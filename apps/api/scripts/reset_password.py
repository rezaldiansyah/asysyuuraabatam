from database import SessionLocal
from models import User
from auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.nik == "999999").first()
if user:
    user.password_hash = get_password_hash("password")
    db.commit()
    print("Password reset to 'password'")
else:
    print("User not found")
