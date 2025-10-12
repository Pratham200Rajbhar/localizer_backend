#!/usr/bin/env python3
"""
Test script for Speech-to-Text functionality
"""
import requests
import json
import os

# Backend URL
BASE_URL = "http://127.0.0.1:8000"
DEMO_AUDIO_FILE = "E:/new_backend/demo.mp3"

def test_auth():
    """Test authentication"""
    # Try to register/login admin user
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Authentication successful")
        return token
    else:
        print("❌ Authentication failed:", response.text)
        # Try to create admin user first
        print("Trying to create admin user...")
        register_data = {
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print("Register response:", register_response.status_code, register_response.text)
        
        # Try login again
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Authentication successful after registration")
            return token
        else:
            print("❌ Authentication still failed:", response.text)
            return None

def test_stt(token):
    """Test STT with demo.mp3"""
    if not os.path.exists(DEMO_AUDIO_FILE):
        print(f"❌ Demo audio file not found: {DEMO_AUDIO_FILE}")
        return
    
    print(f"📁 Testing STT with: {DEMO_AUDIO_FILE}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test without language hint
    print("\n🔍 Testing STT without language hint (auto-detection)...")
    with open(DEMO_AUDIO_FILE, "rb") as audio_file:
        files = {"file": ("demo.mp3", audio_file, "audio/mp3")}
        response = requests.post(f"{BASE_URL}/speech/stt", files=files, headers=headers)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ STT successful!")
        print(f"Transcript: '{result['transcript']}'")
        print(f"Detected Language: {result['language_detected']} ({result['language_name']})")
        print(f"Confidence: {result['confidence']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Model Used: {result['model_used']}")
        if result['segments']:
            print(f"Segments: {len(result['segments'])} segments")
    else:
        print("❌ STT failed!")
        print("Response:", response.text)
        
    # Test with Hindi language hint
    print("\n🔍 Testing STT with Hindi language hint...")
    with open(DEMO_AUDIO_FILE, "rb") as audio_file:
        files = {"file": ("demo.mp3", audio_file, "audio/mp3")}
        data = {"language": "hi"}
        response = requests.post(f"{BASE_URL}/speech/stt", files=files, data=data, headers=headers)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ STT with Hindi hint successful!")
        print(f"Transcript: '{result['transcript']}'")
        print(f"Language: {result['language_detected']} ({result['language_name']})")
        print(f"Confidence: {result['confidence']}")
        print(f"Duration: {result['duration']:.2f}s")
    else:
        print("❌ STT with Hindi hint failed!")
        print("Response:", response.text)

def test_supported_languages():
    """Test supported languages endpoint"""
    print("\n🌍 Testing supported languages endpoint...")
    response = requests.get(f"{BASE_URL}/supported-languages")
    if response.status_code == 200:
        languages = response.json()
        print("✅ Supported languages retrieved successfully!")
        print(f"Total languages: {len(languages)}")
        print("Sample languages:", list(languages.keys())[:10], "...")  # Show first 10
        print("Sample names:", [languages[k] for k in list(languages.keys())[:5]])
    else:
        print("❌ Failed to get supported languages!")
        print("Response:", response.text)

def main():
    print("🚀 Testing Speech-to-Text Backend Implementation")
    print("=" * 50)
    
    # Test authentication
    token = test_auth()
    if not token:
        print("❌ Cannot continue without authentication")
        return
    
    # Test supported languages
    test_supported_languages()
    
    # Test STT
    test_stt(token)
    
    print("\n" + "=" * 50)
    print("🏁 Testing complete!")

if __name__ == "__main__":
    main()