#!/usr/bin/env python3
"""
Test script to verify translation and audio translation fixes
"""

import requests
import json
import time

def test_long_text_translation():
    """Test translation of long text to ensure no truncation"""
    print("🔍 Testing Long Text Translation (No Truncation)")
    print("=" * 60)
    
    # Long text that should trigger chunking
    long_text = """
    This is a comprehensive test of the translation system to ensure that long texts are properly translated without truncation. 
    The system should be able to handle documents with multiple paragraphs and complex sentences. 
    This particular text is designed to exceed the previous limits and test the new chunking system.
    
    The translation engine should now be able to process texts up to 1024 characters in a single chunk, 
    and for longer texts, it should automatically split them into manageable chunks and translate each one separately.
    
    This ensures that users get complete translations of their documents, whether they are short messages or long articles.
    The system should maintain context across chunks and provide high-quality translations for all supported Indian languages.
    
    We are testing this with a realistic scenario where a user might want to translate educational content, 
    technical documentation, or any other lengthy material from English to Hindi, Bengali, Tamil, or any other supported language.
    """
    
    test_cases = [
        {
            "name": "Long Text to Hindi",
            "text": long_text.strip(),
            "source": "en",
            "target": "hi"
        },
        {
            "name": "Long Text to Bengali", 
            "text": long_text.strip(),
            "source": "en",
            "target": "bn"
        },
        {
            "name": "Long Text to Tamil",
            "text": long_text.strip(),
            "source": "en", 
            "target": "ta"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Text length: {len(test_case['text'])} characters")
        
        try:
            response = requests.post(
                "http://localhost:8000/translate",
                json={
                    "text": test_case["text"],
                    "source_language": test_case["source"],
                    "target_languages": [test_case["target"]],
                    "domain": "general",
                    "apply_localization": True
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "results" in result and len(result["results"]) > 0:
                    translation = result["results"][0]
                    translated_text = translation.get("translated_text", "")
                    confidence = translation.get("confidence", 0)
                    processing_time = translation.get("processing_time", 0)
                    
                    print(f"   ✅ Translation successful")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   ⏱️  Processing time: {processing_time:.2f}s")
                    print(f"   📏 Translated length: {len(translated_text)} characters")
                    
                    # Check if translation is complete (not truncated)
                    if len(translated_text) > 100:  # Should be substantial
                        print(f"   ✅ Translation appears complete (not truncated)")
                    else:
                        print(f"   ⚠️  Translation might be truncated")
                    
                    # Show first 100 characters of translation
                    preview = translated_text[:100] + "..." if len(translated_text) > 100 else translated_text
                    print(f"   📄 Preview: {preview}")
                    
                else:
                    print(f"   ❌ No translation results in response")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_audio_translation():
    """Test audio translation with subtitle generation"""
    print("\n🔍 Testing Audio Translation (Subtitle Generation)")
    print("=" * 60)
    
    # Test with a sample audio file if available
    test_file = "testing_files/domo.mp3"  # Adjust path as needed
    
    try:
        with open(test_file, 'rb') as audio_file:
            files = {"file": audio_file}
            data = {
                "language": "en",
                "target_language": "hi", 
                "format": "srt",
                "domain": "general"
            }
            
            print(f"📝 Testing audio file: {test_file}")
            
            response = requests.post(
                "http://localhost:8000/speech/subtitles",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Subtitle generation successful")
                print(f"   📊 Status: {result.get('status', 'unknown')}")
                print(f"   🎯 Detected language: {result.get('detected_language', 'unknown')}")
                print(f"   🎯 Target language: {result.get('target_language', 'unknown')}")
                print(f"   📝 Translated: {result.get('translated', False)}")
                print(f"   📄 Format: {result.get('format', 'unknown')}")
                print(f"   ⏱️  Duration: {result.get('duration_seconds', 0):.2f}s")
                print(f"   📊 Segments: {result.get('segment_count', 0)}")
                
                # Check subtitle content
                subtitle_content = result.get('subtitle_content', '')
                if subtitle_content:
                    print(f"   📏 Subtitle content length: {len(subtitle_content)} characters")
                    
                    # Check if content is complete (not truncated)
                    if len(subtitle_content) > 200:  # Should be substantial
                        print(f"   ✅ Subtitle content appears complete (not truncated)")
                    else:
                        print(f"   ⚠️  Subtitle content might be truncated")
                    
                    # Show first 200 characters
                    preview = subtitle_content[:200] + "..." if len(subtitle_content) > 200 else subtitle_content
                    print(f"   📄 Content preview: {preview}")
                else:
                    print(f"   ⚠️  No subtitle content in response")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
    except FileNotFoundError:
        print(f"   ⚠️  Test file {test_file} not found, skipping audio test")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_language_detection():
    """Test language detection with various texts"""
    print("\n🔍 Testing Language Detection")
    print("=" * 60)
    
    test_cases = [
        {
            "text": "Hello, how are you today? This is a test of the language detection system.",
            "expected": "en"
        },
        {
            "text": "नमस्ते, आप कैसे हैं? यह भाषा पहचान प्रणाली का परीक्षण है।",
            "expected": "hi"
        },
        {
            "text": "আমি ভালো আছি, ধন্যবাদ। এটি ভাষা সনাক্তকরণ সিস্টেমের একটি পরীক্ষা।",
            "expected": "bn"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case['text'][:50]}...'")
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
                
                print(f"   ✅ Detection successful")
                print(f"   📊 Detected: {detected}")
                print(f"   📊 Confidence: {confidence:.2f}")
                
                if detected == test_case["expected"]:
                    print(f"   ✅ Correct detection")
                else:
                    print(f"   ⚠️  Incorrect detection (expected {test_case['expected']})")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Translation and Audio Translation Fixes Test")
    print("=" * 80)
    print("Testing the fixes for incomplete translation responses")
    print("=" * 80)
    
    # Test language detection first
    test_language_detection()
    
    # Test long text translation
    test_long_text_translation()
    
    # Test audio translation
    test_audio_translation()
    
    print("\n" + "=" * 80)
    print("🎯 Test Summary:")
    print("- Language detection should work correctly")
    print("- Long text translations should be complete (no truncation)")
    print("- Audio subtitle generation should return full content")
    print("- All responses should be comprehensive and complete")
    print("=" * 80)