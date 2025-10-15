#!/usr/bin/env python3
"""
Comprehensive Translation Algorithm Testing
Tests translation quality, understanding, and accuracy across different scenarios
"""

import requests
import json
import time
from typing import Dict, List, Any

def test_basic_translation():
    """Test basic translation functionality"""
    print("🔍 Testing Basic Translation")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Simple English to Hindi",
            "text": "Hello, how are you?",
            "source": "en",
            "target": "hi",
            "expected_keywords": ["नमस्ते", "कैसे", "हैं", "आप"]
        },
        {
            "name": "Simple Hindi to English", 
            "text": "नमस्ते, आप कैसे हैं?",
            "source": "hi",
            "target": "en",
            "expected_keywords": ["hello", "how", "are", "you"]
        },
        {
            "name": "Technical Terms",
            "text": "The computer system is running smoothly.",
            "source": "en", 
            "target": "hi",
            "expected_keywords": ["कंप्यूटर", "सिस्टम", "चल", "रहा"]
        },
        {
            "name": "Numbers and Dates",
            "text": "Today is January 15, 2024. The meeting is at 3:30 PM.",
            "source": "en",
            "target": "hi", 
            "expected_keywords": ["आज", "जनवरी", "मीटिंग", "बजे"]
        },
        {
            "name": "Questions",
            "text": "What is your name? Where do you live?",
            "source": "en",
            "target": "hi",
            "expected_keywords": ["क्या", "नाम", "कहाँ", "रहते"]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Source: {test_case['text']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/translate",
                json={
                    "text": test_case["text"],
                    "source_language": test_case["source"],
                    "target_languages": [test_case["target"]],
                    "domain": "general"
                },
                timeout=30
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

def test_context_understanding():
    """Test context understanding and domain-specific translation"""
    print(f"\n🧠 Testing Context Understanding")
    print("=" * 50)
    
    context_tests = [
        {
            "name": "Medical Context",
            "text": "The patient has a fever and needs medication.",
            "source": "en",
            "target": "hi",
            "domain": "healthcare",
            "expected_medical_terms": ["रोगी", "बुखार", "दवा", "जरूरत"]
        },
        {
            "name": "Construction Context", 
            "text": "Wear safety helmet and use proper tools.",
            "source": "en",
            "target": "hi",
            "domain": "construction",
            "expected_terms": ["सुरक्षा", "हेलमेट", "उपकरण", "पहनें"]
        },
        {
            "name": "Education Context",
            "text": "Students should complete their homework and attend classes.",
            "source": "en", 
            "target": "hi",
            "domain": "education",
            "expected_terms": ["छात्र", "गृहकार्य", "कक्षा", "उपस्थित"]
        },
        {
            "name": "Business Context",
            "text": "The quarterly report shows increased revenue and profit margins.",
            "source": "en",
            "target": "hi", 
            "domain": "business",
            "expected_terms": ["रिपोर्ट", "राजस्व", "लाभ", "मार्जिन"]
        }
    ]
    
    for test_case in context_tests:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Domain: {test_case['domain']}")
        print(f"   Text: {test_case['text']}")
        
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
                    confidence = translation.get("confidence", 0)
                    
                    print(f"   ✅ Translation successful")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   📄 Result: {translated_text}")
                    
                    # Check for domain-specific terms
                    found_terms = []
                    for term in test_case["expected_terms"]:
                        if term.lower() in translated_text.lower():
                            found_terms.append(term)
                    
                    if found_terms:
                        print(f"   ✅ Found domain terms: {found_terms}")
                    else:
                        print(f"   ⚠️  No domain terms found: {test_case['expected_terms']}")
                        
                else:
                    print(f"   ❌ No translations returned")
            else:
                print(f"   ❌ Translation failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_grammar_and_syntax():
    """Test grammar and syntax understanding"""
    print(f"\n📚 Testing Grammar and Syntax")
    print("=" * 50)
    
    grammar_tests = [
        {
            "name": "Complex Sentence Structure",
            "text": "Although it was raining heavily, the students continued their outdoor activities because they were determined to complete the project.",
            "source": "en",
            "target": "hi"
        },
        {
            "name": "Conditional Statements",
            "text": "If you study hard, you will pass the exam. However, if you don't study, you might fail.",
            "source": "en", 
            "target": "hi"
        },
        {
            "name": "Passive Voice",
            "text": "The book was written by a famous author and was published last year.",
            "source": "en",
            "target": "hi"
        },
        {
            "name": "Multiple Clauses",
            "text": "The manager, who has been working here for ten years, decided to retire, but the company asked him to stay for another year.",
            "source": "en",
            "target": "hi"
        },
        {
            "name": "Negation and Questions",
            "text": "Don't you think this is a good idea? I don't believe it will work.",
            "source": "en",
            "target": "hi"
        }
    ]
    
    for test_case in grammar_tests:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Text: {test_case['text']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/translate",
                json={
                    "text": test_case["text"],
                    "source_language": test_case["source"],
                    "target_languages": [test_case["target"]],
                    "domain": "general"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = result.get("results", [])
                
                if translations:
                    translation = translations[0]
                    translated_text = translation.get("translated_text", "")
                    confidence = translation.get("confidence", 0)
                    
                    print(f"   ✅ Translation successful")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   📄 Result: {translated_text}")
                    
                    # Basic quality checks
                    if len(translated_text) > 10:  # Should have substantial translation
                        print(f"   ✅ Substantial translation provided")
                    else:
                        print(f"   ⚠️  Translation seems too short")
                        
                    if confidence > 0.5:
                        print(f"   ✅ Good confidence score")
                    else:
                        print(f"   ⚠️  Low confidence score")
                        
                else:
                    print(f"   ❌ No translations returned")
            else:
                print(f"   ❌ Translation failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_cultural_adaptation():
    """Test cultural adaptation and localization"""
    print(f"\n🌍 Testing Cultural Adaptation")
    print("=" * 50)
    
    cultural_tests = [
        {
            "name": "Cultural References",
            "text": "Good morning! How are you doing today?",
            "source": "en",
            "target": "hi",
            "expected_politeness": ["नमस्ते", "सुप्रभात", "आप", "कैसे"]
        },
        {
            "name": "Formal vs Informal",
            "text": "Hey buddy, what's up? vs Good morning, sir. How may I help you?",
            "source": "en",
            "target": "hi"
        },
        {
            "name": "Time References",
            "text": "I will meet you tomorrow at 2 PM in the afternoon.",
            "source": "en",
            "target": "hi",
            "expected_time_terms": ["कल", "दोपहर", "बजे", "मिलूंगा"]
        },
        {
            "name": "Family Relationships",
            "text": "My father's brother is coming to visit us next week.",
            "source": "en",
            "target": "hi",
            "expected_relations": ["पिता", "भाई", "आने", "सप्ताह"]
        }
    ]
    
    for test_case in cultural_tests:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Text: {test_case['text']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/translate",
                json={
                    "text": test_case["text"],
                    "source_language": test_case["source"],
                    "target_languages": [test_case["target"]],
                    "domain": "general"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translations = result.get("results", [])
                
                if translations:
                    translation = translations[0]
                    translated_text = translation.get("translated_text", "")
                    confidence = translation.get("confidence", 0)
                    localized = translation.get("localized", False)
                    
                    print(f"   ✅ Translation successful")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   📊 Localized: {localized}")
                    print(f"   📄 Result: {translated_text}")
                    
                    # Check for cultural adaptation
                    if "expected_politeness" in test_case:
                        found_politeness = []
                        for term in test_case["expected_politeness"]:
                            if term.lower() in translated_text.lower():
                                found_politeness.append(term)
                        
                        if found_politeness:
                            print(f"   ✅ Found polite terms: {found_politeness}")
                        else:
                            print(f"   ⚠️  No polite terms found")
                    
                    if "expected_time_terms" in test_case:
                        found_time = []
                        for term in test_case["expected_time_terms"]:
                            if term.lower() in translated_text.lower():
                                found_time.append(term)
                        
                        if found_time:
                            print(f"   ✅ Found time terms: {found_time}")
                        else:
                            print(f"   ⚠️  No time terms found")
                            
                else:
                    print(f"   ❌ No translations returned")
            else:
                print(f"   ❌ Translation failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_language_detection_accuracy():
    """Test language detection accuracy"""
    print(f"\n🔍 Testing Language Detection")
    print("=" * 50)
    
    detection_tests = [
        {
            "text": "Hello, how are you today?",
            "expected": "en"
        },
        {
            "text": "नमस्ते, आप कैसे हैं?",
            "expected": "hi"
        },
        {
            "text": "আমি ভালো আছি, ধন্যবাদ।",
            "expected": "bn"
        },
        {
            "text": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",
            "expected": "ta"
        },
        {
            "text": "नमस्कार, तपाईं कसरी हुनुहुन्छ?",
            "expected": "ne"
        },
        {
            "text": "This is a mixed text with English and हिंदी words.",
            "expected": "en"  # Should detect dominant language
        }
    ]
    
    for test_case in detection_tests:
        print(f"\n📝 Testing: '{test_case['text'][:30]}...'")
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

def main():
    """Run all translation algorithm tests"""
    print("🚀 Comprehensive Translation Algorithm Testing")
    print("=" * 70)
    
    # Test basic translation
    test_basic_translation()
    
    # Test context understanding
    test_context_understanding()
    
    # Test grammar and syntax
    test_grammar_and_syntax()
    
    # Test cultural adaptation
    test_cultural_adaptation()
    
    # Test language detection
    test_language_detection_accuracy()
    
    print(f"\n" + "=" * 70)
    print("📊 Translation algorithm testing completed!")
    print("🔍 Review the results above to identify any issues with understanding or accuracy.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
