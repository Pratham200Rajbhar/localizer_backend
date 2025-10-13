#!/usr/bin/env python3
"""
Test just the feedback system specifically
"""

import asyncio
import httpx
import json

async def test_feedback_only():
    """Test only the feedback system"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Feedback System Only")
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
        
        # Test feedback with file_id only
        feedback_data = {
            "file_id": 1,  # Use simple file ID
            "rating": 4,
            "comments": "Good translation quality",
            "corrections": {"suggestion": "Minor improvements needed"}
        }
        
        print(f"Submitting feedback: {feedback_data}")
        
        response = await client.post(
            f"{base_url}/feedback",
            headers=headers,
            json=feedback_data
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Feedback submitted successfully: {result}")
        else:
            print(f"❌ Feedback failed")
            
        # Test with translation_id
        feedback_data2 = {
            "translation_id": 1,
            "rating": 5,
            "comments": "Excellent work"
        }
        
        print(f"\nTesting with translation_id: {feedback_data2}")
        
        response2 = await client.post(
            f"{base_url}/feedback",
            headers=headers,
            json=feedback_data2
        )
        
        print(f"Response status: {response2.status_code}")
        print(f"Response text: {response2.text}")

if __name__ == "__main__":
    asyncio.run(test_feedback_only())