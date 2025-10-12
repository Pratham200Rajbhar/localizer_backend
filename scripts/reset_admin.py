#!/usr/bin/env python3
"""
Script to reset admin user password
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def reset_admin_password():
    """Reset admin user password"""
    db = SessionLocal()
    
    try:
        # Find admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("Admin user not found!")
            return False
        
        # Update password
        admin_user.password_hash = hash_password("admin123")
        db.commit()
        
        print("Admin password reset successfully!")
        return True
    
    except Exception as e:
        print(f"Error resetting password: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    reset_admin_password()