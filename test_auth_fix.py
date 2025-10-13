#!/usr/bin/env python3
"""
Test script to verify authentication works with plain text passwords
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from app.core.config import get_settings
from app.core.db import get_db, engine
from app.core.db import Base
from app.models.user import User
from sqlalchemy.orm import sessionmaker

settings = get_settings()

def create_test_user():
    """Create a test user for authentication testing"""
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Create session
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Check if test user exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        # Create test user with plain text password
        test_user = User(
            username="testuser",
            password="testpass123",
            role="uploader"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Test user created: {test_user.username} (ID: {test_user.id})")
        print(f"   Password: {test_user.password}")
        print(f"   Role: {test_user.role}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        return False

async def test_authentication():
    """Test the authentication endpoints"""
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test login
            print("\n🔐 Testing login...")
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = await client.post(
                f"{base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Login successful!")
                print(f"   Access Token: {result['access_token'][:50]}...")
                print(f"   Token Type: {result['token_type']}")
                print(f"   User: {result['user']['username']} ({result['user']['role']})")
                
                # Test protected endpoint
                print("\n🔒 Testing protected endpoint...")
                headers = {"Authorization": f"Bearer {result['access_token']}"}
                
                me_response = await client.get(
                    f"{base_url}/auth/me",
                    headers=headers
                )
                
                if me_response.status_code == 200:
                    user_info = me_response.json()
                    print("✅ Protected endpoint access successful!")
                    print(f"   User info: {user_info}")
                else:
                    print(f"❌ Protected endpoint failed: {me_response.status_code}")
                    print(f"   Response: {me_response.text}")
                
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Authentication System with Plain Text Passwords")
    print("=" * 60)
    
    # Create test user
    if not create_test_user():
        return
    
    # Check if server is running
    import subprocess
    import time
    
    print("\n🚀 Starting FastAPI server...")
    try:
        # Start the server in the background
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
            cwd=str(Path(__file__).parent)
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Run authentication tests
        asyncio.run(test_authentication())
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
    except Exception as e:
        print(f"❌ Server start failed: {e}")
    finally:
        # Clean up server process
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

if __name__ == "__main__":
    main()