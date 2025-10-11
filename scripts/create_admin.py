#!/usr/bin/env python3
"""
Script to create initial admin user
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def create_admin_user(username: str, email: str, password: str):
    """Create admin user"""
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"Admin user '{username}' created successfully!")
        return True
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    create_admin_user(username, email, password)

