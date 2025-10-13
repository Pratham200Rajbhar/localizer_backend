"""
Quick STT test to debug the issue
"""
import requests
import os

BASE_URL = "http://localhost:8000"
DEMO_AUDIO_PATH = "E:/new_backend/demo.mp3"

def test_stt():
    print("Testing STT with debug info...")
    
    if not os.path.exists(DEMO_AUDIO_PATH):
        print(f"Audio file not found: {DEMO_AUDIO_PATH}")
        return
    
    print(f"Audio file size: {os.path.getsize(DEMO_AUDIO_PATH)} bytes")
    
    try:
        with open(DEMO_AUDIO_PATH, 'rb') as f:
            files = {'file': ('demo.mp3', f, 'audio/mpeg')}
            print("Sending request...")
            response = requests.post(f"{BASE_URL}/speech/stt", files=files)
            
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stt()