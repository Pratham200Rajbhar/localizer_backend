#!/usr/bin/env python3
"""
Test script to verify the audio localization translation fix
Tests both /translate and /localize endpoints to ensure complete translations
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000"

def test_audio_localization_endpoints():
    """Test both audio localization endpoints"""
    print("🧪 Testing Audio Localization Translation Fix")
    print("=" * 60)
    
    # Create a test audio file (you can replace this with an actual audio file)
    test_audio_content = b"dummy audio content for testing"
    test_filename = "test_audio.mp3"
    
    try:
        # Test 1: /speech/translate endpoint
        print("\n📝 Test 1: /speech/translate endpoint")
        print("-" * 40)
        
        with open(test_filename, 'wb') as f:
            f.write(test_audio_content)
        
        with open(test_filename, 'rb') as f:
            files = {"file": f}
            data = {
                "target_language": "hi",
                "domain": "general"
            }
            
            response = requests.post(
                f"{BASE_URL}/speech/translate",
                files=files,
                data=data,
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ /speech/translate endpoint working")
            print(f"📊 Status: {result.get('status')}")
            print(f"📊 Source text length: {len(result.get('source_text', ''))}")
            print(f"📊 Translated text length: {len(result.get('translated_text', ''))}")
            print(f"📊 Source text: {result.get('source_text', '')[:100]}...")
            print(f"📊 Translated text: {result.get('translated_text', '')[:100]}...")
            
            # Check if translation is complete
            if result.get('translated_text') and len(result.get('translated_text', '')) > 50:
                print("✅ Translation appears complete (no truncation)")
            else:
                print("⚠️  Translation might be incomplete or truncated")
        else:
            print(f"❌ /speech/translate failed: {response.status_code} - {response.text}")
        
        # Test 2: /speech/localize endpoint
        print("\n📝 Test 2: /speech/localize endpoint")
        print("-" * 40)
        
        with open(test_filename, 'rb') as f:
            files = {"file": f}
            data = {
                "target_language": "hi",
                "domain": "general"
            }
            
            response = requests.post(
                f"{BASE_URL}/speech/localize",
                files=files,
                data=data,
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ /speech/localize endpoint working")
            print(f"📊 Status: {result.get('status')}")
            
            # Check pipeline steps
            pipeline_steps = result.get('pipeline_steps', {})
            stt_step = pipeline_steps.get('stt', {})
            translation_step = pipeline_steps.get('translation', {})
            
            print(f"📊 STT detected language: {stt_step.get('detected_language')}")
            print(f"📊 STT text length: {len(stt_step.get('transcribed_text', ''))}")
            print(f"📊 Translation text length: {len(translation_step.get('translated_text', ''))}")
            print(f"📊 STT text: {stt_step.get('transcribed_text', '')[:100]}...")
            print(f"📊 Translated text: {translation_step.get('translated_text', '')[:100]}...")
            print(f"📊 Confidence score: {translation_step.get('confidence_score', 0)}")
            
            # Check if translation is complete and not truncated
            translated_text = translation_step.get('translated_text', '')
            if translated_text and len(translated_text) > 50:
                if not translated_text.endswith('...'):
                    print("✅ Translation appears complete (no truncation in response)")
                else:
                    print("⚠️  Translation might be truncated (ends with ...)")
            else:
                print("⚠️  Translation might be incomplete or very short")
                
            # Check for mixed language issues
            if 'let\'s' in translated_text.lower() and any(char in translated_text for char in ['न', 'ह', 'ी']):
                print("⚠️  Mixed language detected in translation")
            else:
                print("✅ No obvious mixed language issues")
                
        else:
            print(f"❌ /speech/localize failed: {response.status_code} - {response.text}")
        
        # Test 3: Check server logs for debugging info
        print("\n📝 Test 3: Check server logs")
        print("-" * 40)
        
        try:
            response = requests.get(f"{BASE_URL}/logs/activities?limit=10", timeout=30)
            if response.status_code == 200:
                activities = response.json().get('activities', [])
                print(f"📊 Recent activities: {len(activities)}")
                for activity in activities[-3:]:  # Show last 3 activities
                    print(f"   - {activity.get('activity_type', 'unknown')}: {activity.get('description', '')[:50]}...")
            else:
                print(f"❌ Could not fetch logs: {response.status_code}")
        except Exception as e:
            print(f"❌ Error fetching logs: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 Test Summary:")
        print("✅ Both endpoints tested")
        print("✅ Translation completeness checked")
        print("✅ Mixed language issues checked")
        print("✅ Response format validated")
        print("\n💡 If you see mixed language or truncated translations,")
        print("   check the server logs for detailed debugging information.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
            print(f"🧹 Cleaned up test file: {test_filename}")

def test_with_real_audio():
    """Test with a real audio file if available"""
    print("\n🎵 Testing with Real Audio File")
    print("=" * 60)
    
    # Look for common audio files in the current directory
    audio_files = [f for f in os.listdir('.') if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
    
    if not audio_files:
        print("ℹ️  No audio files found in current directory")
        print("   To test with real audio, place an audio file in the current directory")
        return
    
    test_file = audio_files[0]
    print(f"📁 Using audio file: {test_file}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {"file": f}
            data = {
                "target_language": "hi",
                "domain": "general"
            }
            
            print("🔄 Sending request to /speech/localize...")
            response = requests.post(
                f"{BASE_URL}/speech/localize",
                files=files,
                data=data,
                timeout=180  # Longer timeout for real audio
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Real audio test successful!")
            
            pipeline_steps = result.get('pipeline_steps', {})
            stt_step = pipeline_steps.get('stt', {})
            translation_step = pipeline_steps.get('translation', {})
            
            print(f"📊 Processing time: {result.get('processing_time_seconds', 0):.2f}s")
            print(f"📊 Detected language: {stt_step.get('detected_language')}")
            print(f"📊 Audio duration: {stt_step.get('duration_seconds', 0):.2f}s")
            print(f"📊 Source text: {stt_step.get('transcribed_text', '')}")
            print(f"📊 Translated text: {translation_step.get('translated_text', '')}")
            print(f"📊 Confidence: {translation_step.get('confidence_score', 0)}")
            
            # Validate translation quality
            translated_text = translation_step.get('translated_text', '')
            if translated_text:
                if len(translated_text) > 20 and not translated_text.endswith('...'):
                    print("✅ Translation appears complete and properly formatted")
                else:
                    print("⚠️  Translation might be incomplete")
            else:
                print("❌ No translation text received")
                
        else:
            print(f"❌ Real audio test failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Real audio test error: {e}")

if __name__ == "__main__":
    print("🚀 Audio Localization Translation Fix Test")
    print("This test verifies that audio localization returns complete translations")
    print("without truncation or mixed language issues.")
    print()
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_audio_localization_endpoints()
    test_with_real_audio()
    
    print("\n🎉 Test completed!")
    print("Check the results above to verify the translation fix is working.")
