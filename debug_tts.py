"""
Quick TTS test to debug the issue
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_tts():
    print("Testing TTS with debug info...")
    
    data = {
        "text": "नमस्ते, यह एक परीक्षण संदेश है।",
        "language": "hi"
    }
    
    try:
        print("Sending TTS request...")
        response = requests.post(f"{BASE_URL}/speech/tts", json=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tts()