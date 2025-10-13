#!/usr/bin/env python3
"""
Test the simple feedback endpoint
"""

import asyncio
import httpx

async def test_simple_feedback():
    """Test the simple feedback endpoint"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Simple Feedback Endpoint")
    print("=" * 40)
    
    # Login as reviewer
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_data = {
            "username": "testreviewer",
            "password": "reviewer123"
        }
        
        response = await client.post(
            f"{base_url}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return
        
        token = response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Login successful")
        
        # Test simple feedback
        feedback_data = {
            "rating": 4,
            "comments": "Good system performance overall"
        }
        
        print(f"Submitting simple feedback: {feedback_data}")
        
        response = await client.post(
            f"{base_url}/feedback",  # Try the simple endpoint directly
            headers=headers,
            json=feedback_data
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Simple feedback submitted successfully: {result}")
            return True
        else:
            print(f"❌ Simple feedback failed")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_feedback())
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")