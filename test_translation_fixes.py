#!/usr/bin/env python3
"""
Test the translation algorithm fixes
"""

import requests
import json

def test_english_detection_fix():
    """Test if English detection is now working correctly"""
    print("🔍 Testing English Detection Fix")
    print("=" * 50)
    
    test_cases = [
        {
            "text": "Hello, how are you today?",
            "expected": "en"
        },
        {
            "text": "This is a mixed text with English and हिंदी words.",
            "expected": "en"  # Should detect dominant language
        },
        {
            "text": "The computer system is running smoothly.",
            "expected": "en"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case['text']}'")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/detect-language",
                json={"text": test_case["text"]},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                detected = result.get("detected_language", "unknown")
                confidence = result.get("confidence", 0)
                language_name = result.get("language_name", "Unknown")
                
                print(f"   ✅ Detection successful")
                print(f"   📊 Detected: {detected} ({language_name})")
                print(f"   📊 Confidence: {confidence:.2f}")
                
                if detected == test_case["expected"]:
                    print(f"   ✅ Correct detection!")
                else:
                    print(f"   ❌ Incorrect detection (expected: {test_case['expected']})")
                    
            else:
                print(f"   ❌ Detection failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_hindi_to_english_translation():
    """Test Hindi to English translation with increased timeout"""
    print(f"\n🔄 Testing Hindi to English Translation")
    print("=" * 50)
    
    test_cases = [
        {
            "text": "नमस्ते, आप कैसे हैं?",
            "expected_keywords": ["hello", "how", "are", "you"]
        },
        {
            "text": "मैं एक छात्र हूँ।",
            "expected_keywords": ["i", "am", "student"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case['text']}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/translate",
                json={
                    "text": test_case["text"],
                    "source_language": "hi",
                    "target_languages": ["en"],
                    "domain": "general"
                },
                timeout=60  # Increased timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = result.get("results", [])
                
                if translations:
                    translation = translations[0]
                    translated_text = translation.get("translated_text", "")
                    confidence = translation.get("confidence", 0)
                    model_used = translation.get("model_used", "unknown")
                    
                    print(f"   ✅ Translation successful")
                    print(f"   📊 Model: {model_used}")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   📄 Result: {translated_text}")
                    
                    # Check for expected keywords
                    found_keywords = []
                    for keyword in test_case["expected_keywords"]:
                        if keyword.lower() in translated_text.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"   ✅ Found expected keywords: {found_keywords}")
                    else:
                        print(f"   ⚠️  No expected keywords found: {test_case['expected_keywords']}")
                        
                else:
                    print(f"   ❌ No translations returned")
            else:
                print(f"   ❌ Translation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_localization():
    """Test if localization is working"""
    print(f"\n🌍 Testing Localization")
    print("=" * 50)
    
    test_cases = [
        {
            "text": "Good morning, sir. How may I help you?",
            "source": "en",
            "target": "hi",
            "domain": "business",
            "expected_honorifics": ["साहब", "जी"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case['text']}'")
        print(f"   Domain: {test_case['domain']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/translate",
                json={
                    "text": test_case["text"],
                    "source_language": test_case["source"],
                    "target_languages": [test_case["target"]],
                    "domain": test_case["domain"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = result.get("results", [])
                
                if translations:
                    translation = translations[0]
                    translated_text = translation.get("translated_text", "")
                    localized = translation.get("localized", False)
                    confidence = translation.get("confidence", 0)
                    
                    print(f"   ✅ Translation successful")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   📊 Localized: {localized}")
                    print(f"   📄 Result: {translated_text}")
                    
                    # Check for honorifics
                    found_honorifics = []
                    for honorific in test_case["expected_honorifics"]:
                        if honorific in translated_text:
                            found_honorifics.append(honorific)
                    
                    if found_honorifics:
                        print(f"   ✅ Found honorifics: {found_honorifics}")
                    else:
                        print(f"   ⚠️  No honorifics found: {test_case['expected_honorifics']}")
                        
                else:
                    print(f"   ❌ No translations returned")
            else:
                print(f"   ❌ Translation failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Run all translation fix tests"""
    print("🚀 Testing Translation Algorithm Fixes")
    print("=" * 70)
    
    # Test English detection fix
    test_english_detection_fix()
    
    # Test Hindi to English translation
    test_hindi_to_english_translation()
    
    # Test localization
    test_localization()
    
    print(f"\n" + "=" * 70)
    print("📊 Translation fix testing completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
