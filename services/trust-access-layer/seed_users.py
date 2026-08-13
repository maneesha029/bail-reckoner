import uuid
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import User
from auth import get_password_hash

def seed_users():
    init_db()
    db: Session = SessionLocal()
    
    users = [
        {"username": "demo_judge", "password": "password123", "role": "judge"},
        {"username": "demo_legal_aid", "password": "password123", "role": "legal_aid"},
        {"username": "demo_jail_officer", "password": "password123", "role": "jail_officer"},
        {"username": "demo_admin", "password": "password123", "role": "admin"}
    ]
    
    try:
        for u in users:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                new_user = User(
                    user_id=uuid.uuid4(),
                    username=u["username"],
                    password_hash=get_password_hash(u["password"]),
                    role=u["role"]
                )
                db.add(new_user)
        db.commit()
        print("Demo users seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
