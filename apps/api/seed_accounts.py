from database import SessionLocal
from models import Account

db = SessionLocal()

accounts = [
    {"code": "1-1001", "name": "Kas Operasional", "type": "ASSET"},
    {"code": "1-1002", "name": "Bank BCA", "type": "ASSET"},
    {"code": "4-1001", "name": "Pendapatan SPP", "type": "REVENUE"},
    {"code": "4-1002", "name": "Pendapatan Pendaftaran", "type": "REVENUE"},
    {"code": "5-1001", "name": "Beban Listrik & Air", "type": "EXPENSE"},
    {"code": "5-1002", "name": "Gaji Guru", "type": "EXPENSE"},
]

for acc in accounts:
    exists = db.query(Account).filter(Account.code == acc["code"]).first()
    if not exists:
        db.add(Account(**acc))
        print(f"Created account: {acc['name']}")
    else:
        print(f"Account exists: {acc['name']}")

db.commit()
db.close()
