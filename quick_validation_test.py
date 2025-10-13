#!/usr/bin/env python3
"""
Quick Translation Test - Verify all fixes are working
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_translation_fixes():
    print("🔧 TESTING TRANSLATION FIXES")
    print("="*40)
    
    # Test data
    test_cases = [
        {
            "text": "Hello, how are you?",
            "source_language": "en",
            "target_languages": ["hi", "bn", "ta"],
            "description": "English to Indian languages"
        },
        {
            "text": "The weather is nice today",
            "source_language": "en", 
            "target_languages": ["te", "gu", "mr"],
            "description": "Weather-related translation"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json=test_case,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS - {len(data.get('results', []))} translations")
                
                for result in data.get('results', []):
                    lang = result.get('target_language', 'unknown')
                    translated = result.get('translated_text', 'N/A')
                    model = result.get('model_used', 'unknown')
                    
                    if result.get('error'):
                        print(f"  ⚠️ {lang}: ERROR - {result['error']}")
                        results.append(f"Error in {lang}")
                    else:
                        print(f"  ✅ {lang}: '{translated}' (Model: {model})")
                        results.append(f"Success in {lang}")
                        
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                results.append(f"HTTP Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR - {e}")
            results.append(f"Exception: {str(e)}")
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 SUMMARY:")
    success_count = sum(1 for r in results if "Success" in r)
    total_count = len(results) 
    
    print(f"Successful translations: {success_count}/{total_count}")
    
    if success_count > 0:
        print("🎉 Translation system is working!")
    else:
        print("⚠️ Translation system needs more fixes")
        
    return results

def test_speech_to_text():
    print("\n🎤 TESTING SPEECH-TO-TEXT")
    print("="*30)
    
    demo_file = "E:/new_backend/demo.mp3"
    try:
        with open(demo_file, 'rb') as f:
            files = {'file': ('demo.mp3', f, 'audio/mpeg')}
            response = requests.post(f"{BASE_URL}/speech/stt", files=files, timeout=30)
            
        if response.status_code == 200:
            data = response.json()
            transcript = data.get('transcript', '')
            print(f"✅ STT SUCCESS - Transcript length: {len(transcript)} characters")
            print(f"   Sample: '{transcript[:100]}...'")
            return True
        else:
            print(f"❌ STT FAILED - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ STT ERROR - {e}")
        return False

def test_text_to_speech():
    print("\n🔊 TESTING TEXT-TO-SPEECH")
    print("="*30)
    
    test_data = {"text": "नमस्ते, यह एक परीक्षण है।", "language": "hi"}
    
    try:
        response = requests.post(f"{BASE_URL}/speech/tts", json=test_data, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            audio_path = data.get('audio_path', '')
            print(f"✅ TTS SUCCESS - Audio file: {audio_path}")
            return True
        else:
            print(f"❌ TTS FAILED - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ TTS ERROR - {e}")
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE SYSTEM VALIDATION")
    print("="*50)
    
    # Test each component
    translation_results = test_translation_fixes()
    stt_working = test_speech_to_text()
    tts_working = test_text_to_speech()
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT:")
    print("="*30)
    
    translation_success = sum(1 for r in translation_results if "Success" in r) > 0
    
    print(f"Translation Engine: {'✅ WORKING' if translation_success else '❌ NEEDS FIX'}")
    print(f"Speech-to-Text: {'✅ WORKING' if stt_working else '❌ NEEDS FIX'}")
    print(f"Text-to-Speech: {'✅ WORKING' if tts_working else '❌ NEEDS FIX'}")
    
    overall_status = translation_success and stt_working
    print(f"\nOverall System Status: {'🎉 PRODUCTION READY' if overall_status else '🔧 NEEDS MORE FIXES'}")