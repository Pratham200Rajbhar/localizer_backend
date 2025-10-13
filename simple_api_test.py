#!/usr/bin/env python3
"""
Direct API Test - Test individual endpoints with shorter timeouts
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test basic health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_languages():
    """Test supported languages endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/supported-languages", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Languages endpoint working - {data.get('total_count', 0)} languages")
            return True
        else:
            print(f"❌ Languages endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Languages endpoint error: {e}")
        return False

def test_single_translation():
    """Test simple translation with very short text"""
    try:
        data = {
            "text": "Hello",
            "source_language": "en", 
            "target_languages": ["hi"],
            "domain": "general"
        }
        
        response = requests.post(f"{BASE_URL}/translate", json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            translations = result.get('results', [])
            
            if translations and len(translations) > 0:
                translation = translations[0]
                translated_text = translation.get('translated_text', '')
                model_used = translation.get('model_used', 'unknown')
                
                print(f"✅ Translation working: 'Hello' -> '{translated_text}' (Model: {model_used})")
                return True
            else:
                print("❌ Translation returned no results")
                return False
        else:
            print(f"❌ Translation failed: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIRECT API ENDPOINT TESTING")
    print("="*40)
    
    health_ok = test_health()
    languages_ok = test_languages()
    translation_ok = test_single_translation()
    
    print(f"\n📊 RESULTS:")
    print(f"Health: {'✅' if health_ok else '❌'}")
    print(f"Languages: {'✅' if languages_ok else '❌'}")
    print(f"Translation: {'✅' if translation_ok else '❌'}")
    
    if health_ok and languages_ok:
        print("\n🎯 Basic endpoints are working!")
        if translation_ok:
            print("🎉 Translation is also working - fixes successful!")
        else:
            print("⚠️ Translation still needs debugging")
    else:
        print("\n❌ Basic endpoints not working - server issues")