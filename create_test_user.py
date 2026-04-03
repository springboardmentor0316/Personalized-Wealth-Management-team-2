#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import User
from auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if test user exists
        user = db.query(User).filter(User.email == 'test@example.com').first()
        if not user:
            # Create test user
            user = User(
                email='test@example.com',
                full_name='Test User',
                hashed_password=get_password_hash('password123')
            )
            db.add(user)
            db.commit()
            print("✅ Test user created successfully!")
            print("📝 Email: test@example.com")
            print("🔑 Password: password123")
        else:
            print("✅ Test user already exists")
            print("📝 Email: test@example.com")
            print("🔑 Password: password123")
        
        # List all users
        users = db.query(User).all()
        print(f"\n📊 Total users in database: {len(users)}")
        for user in users:
            print(f"   - {user.email} ({user.full_name})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
