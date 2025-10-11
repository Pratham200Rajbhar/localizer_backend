#!/usr/bin/env python3
"""
🚀 Quick API Test Runner
Simple script to run essential API tests quickly
"""

import requests
import os
import time

BASE_URL = "http://127.0.0.1:8000"

def quick_test():
    """Run essential API tests quickly"""
    print("🚀 QUICK API TEST RUNNER")
    print("=" * 40)
    
    # Get token
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication: OK")
    except:
        print("❌ Authentication: FAILED")
        return
    
    # Test translation
    try:
        response = requests.post(f"{BASE_URL}/translate", 
            json={"text": "Hello", "source_language": "en", "target_languages": ["hi"]}, 
            headers=headers)
        if response.status_code == 200:
            print("✅ Translation: OK")
        else:
            print(f"❌ Translation: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Translation: FAILED ({e})")
    
    # Test TTS
    try:
        response = requests.post(f"{BASE_URL}/speech/tts", 
            json={"text": "नमस्ते", "language": "hi", "voice": "female"}, 
            headers=headers)
        if response.status_code == 200:
            print("✅ Text-to-Speech: OK")
        else:
            print(f"❌ Text-to-Speech: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Text-to-Speech: FAILED ({e})")
    
    # Test health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health Check: OK")
        else:
            print(f"❌ Health Check: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Health Check: FAILED ({e})")
    
    print("\n🎉 Quick test completed!")

if __name__ == "__main__":
    quick_test()