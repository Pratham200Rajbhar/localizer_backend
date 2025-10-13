"""
Comprehensive API Testing Script
Tests all endpoints with real functionality
"""
import requests
import json
import os
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
DEMO_AUDIO_PATH = "E:/new_backend/demo.mp3"

class APITester:
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        
    def test_health(self):
        """Test health endpoint"""
        print("🏥 Testing Health Endpoint...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                self.results['health'] = {'status': 'success', 'response': response.json()}
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.results['health'] = {'status': 'failed', 'error': f"Status: {response.status_code}"}
                return False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            self.results['health'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_supported_languages(self):
        """Test supported languages endpoint"""
        print("\n🌏 Testing Supported Languages Endpoint...")
        try:
            response = self.session.get(f"{BASE_URL}/supported-languages")
            if response.status_code == 200:
                languages = response.json()
                print(f"✅ Supported languages: {len(languages)} languages available")
                print(f"Languages: {list(languages.keys())[:5]}... (showing first 5)")
                self.results['supported_languages'] = {'status': 'success', 'count': len(languages)}
                return True
            else:
                print(f"❌ Supported languages failed: {response.status_code}")
                self.results['supported_languages'] = {'status': 'failed', 'error': f"Status: {response.status_code}"}
                return False
        except Exception as e:
            print(f"❌ Supported languages error: {e}")
            self.results['supported_languages'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_language_detection(self):
        """Test language detection endpoint"""
        print("\n🔍 Testing Language Detection Endpoint...")
        try:
            test_texts = [
                "Hello, how are you?",
                "नमस्ते, आप कैसे हैं?",
                "வணக்கम், நீங்கள் எப்படி இருக்கிறீர்கள்?"
            ]
            
            for i, text in enumerate(test_texts):
                data = {"text": text}
                response = self.session.post(f"{BASE_URL}/detect-language", json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Text {i+1}: Detected language: {result.get('detected_language', 'unknown')}")
                else:
                    print(f"❌ Language detection failed for text {i+1}: {response.status_code}")
                    
            self.results['language_detection'] = {'status': 'success'}
            return True
            
        except Exception as e:
            print(f"❌ Language detection error: {e}")
            self.results['language_detection'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_file_upload(self):
        """Test file upload functionality"""
        print("\n📁 Testing File Upload Endpoint...")
        try:
            # Create a test text file
            test_content = "This is a comprehensive test file for translation. Hello world! How are you doing today? This should be enough text to translate properly."
            test_file_path = "test_upload.txt"
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test_upload.txt', f, 'text/plain')}
                data = {'domain': 'general'}
                response = self.session.post(f"{BASE_URL}/content/upload", files=files, data=data)
            
            # Clean up
            os.remove(test_file_path)
            
            if response.status_code in [200, 201]:
                result = response.json()
                file_id = result.get('id')  # Changed from 'file_id' to 'id'
                print(f"✅ File uploaded successfully. File ID: {file_id}")
                self.results['file_upload'] = {'status': 'success', 'file_id': file_id}
                return file_id
            else:
                print(f"❌ File upload failed: {response.status_code} - {response.text}")
                self.results['file_upload'] = {'status': 'failed', 'error': response.text}
                return None
                
        except Exception as e:
            print(f"❌ File upload error: {e}")
            self.results['file_upload'] = {'status': 'error', 'error': str(e)}
            return None
    
    def test_translation(self, file_id=None):
        """Test translation endpoint"""
        print("\n🔄 Testing Translation Endpoint...")
        try:
            if file_id:
                # Test with uploaded file
                data = {
                    "file_id": file_id,
                    "source_language": "en",
                    "target_languages": ["hi", "ta", "bn"],
                    "domain": "general"
                }
                response = self.session.post(f"{BASE_URL}/translate", json=data)
            else:
                # Test with direct text
                data = {
                    "text": "Hello, this is a test translation.",
                    "source_language": "en",
                    "target_languages": ["hi", "ta"],
                    "domain": "general"
                }
                response = self.session.post(f"{BASE_URL}/translate", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Translation successful. Job ID: {result.get('job_id', 'N/A')}")
                if 'translations' in result:
                    print(f"Translations generated for {len(result['translations'])} languages")
                self.results['translation'] = {'status': 'success', 'job_id': result.get('job_id')}
                return True
            else:
                print(f"❌ Translation failed: {response.status_code} - {response.text}")
                self.results['translation'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"❌ Translation error: {e}")
            self.results['translation'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_speech_to_text(self):
        """Test speech-to-text endpoint"""
        print("\n🎤 Testing Speech-to-Text (STT) Endpoint...")
        try:
            if not os.path.exists(DEMO_AUDIO_PATH):
                print(f"❌ Demo audio file not found: {DEMO_AUDIO_PATH}")
                self.results['stt'] = {'status': 'error', 'error': 'Demo file not found'}
                return False
            
            with open(DEMO_AUDIO_PATH, 'rb') as f:
                files = {'file': ('demo.mp3', f, 'audio/mpeg')}
                response = self.session.post(f"{BASE_URL}/speech/stt", files=files)
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('transcript', '')
                print(f"✅ STT successful. Transcript: '{transcript[:100]}...'")
                self.results['stt'] = {'status': 'success', 'transcript_length': len(transcript)}
                return True
            else:
                print(f"❌ STT failed: {response.status_code} - {response.text}")
                self.results['stt'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"❌ STT error: {e}")
            self.results['stt'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_text_to_speech(self):
        """Test text-to-speech endpoint"""
        print("\n🔊 Testing Text-to-Speech (TTS) Endpoint...")
        try:
            data = {
                "text": "नमस्ते, यह एक परीक्षण संदेश है।",
                "language": "hi"
            }
            response = self.session.post(f"{BASE_URL}/speech/tts", json=data)
            
            if response.status_code == 200:
                result = response.json()
                audio_path = result.get('audio_path', '')
                print(f"✅ TTS successful. Audio saved to: {audio_path}")
                self.results['tts'] = {'status': 'success', 'audio_path': audio_path}
                return True
            else:
                print(f"❌ TTS failed: {response.status_code} - {response.text}")
                self.results['tts'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"❌ TTS error: {e}")
            self.results['tts'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_feedback(self):
        """Test feedback endpoint"""
        print("\n💬 Testing Feedback Endpoint...")
        try:
            data = {
                "content": "This is test feedback",
                "rating": 4,
                "comments": "Translation quality is good"
            }
            response = self.session.post(f"{BASE_URL}/feedback", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Feedback submitted successfully. ID: {result.get('id', 'N/A')}")
                self.results['feedback'] = {'status': 'success'}
                return True
            else:
                print(f"❌ Feedback failed: {response.status_code} - {response.text}")
                self.results['feedback'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"❌ Feedback error: {e}")
            self.results['feedback'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_localization(self):
        """Test localization/context endpoint"""
        print("\n🌍 Testing Localization/Context Endpoint...")
        try:
            params = {
                "text": "Safety equipment required",
                "domain": "construction", 
                "language": "hi"
            }
            response = self.session.post(f"{BASE_URL}/localize/context", params=params)
            
            if response.status_code == 200:
                result = response.json()
                localized_text = result.get('localized_text', '')
                print(f"✅ Localization successful: '{localized_text}'")
                self.results['localization'] = {'status': 'success'}
                return True
            else:
                print(f"❌ Localization failed: {response.status_code} - {response.text}")
                self.results['localization'] = {'status': 'failed', 'error': response.text}
                return False
                
        except Exception as e:
            print(f"❌ Localization error: {e}")
            self.results['localization'] = {'status': 'error', 'error': str(e)}
            return False
    
    def test_metrics(self):
        """Test metrics endpoint"""
        print("\n📊 Testing Metrics Endpoint...")
        try:
            response = self.session.get(f"{BASE_URL}/metrics")
            
            if response.status_code == 200:
                print("✅ Metrics endpoint working")
                print(f"Response length: {len(response.text)} characters")
                self.results['metrics'] = {'status': 'success'}
                return True
            else:
                print(f"❌ Metrics failed: {response.status_code}")
                self.results['metrics'] = {'status': 'failed', 'error': f"Status: {response.status_code}"}
                return False
                
        except Exception as e:
            print(f"❌ Metrics error: {e}")
            self.results['metrics'] = {'status': 'error', 'error': str(e)}
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive API Testing...")
        print("=" * 50)
        
        # Basic connectivity test
        if not self.test_health():
            print("❌ Server not responding. Please ensure the server is running on port 8000.")
            return
        
        # Test all endpoints
        self.test_supported_languages()
        self.test_language_detection()
        
        file_id = self.test_file_upload()
        self.test_translation(file_id)
        
        self.test_speech_to_text()
        self.test_text_to_speech()
        self.test_feedback()
        self.test_localization()
        self.test_metrics()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'success')
        failed_tests = sum(1 for r in self.results.values() if r['status'] == 'failed')
        error_tests = sum(1 for r in self.results.values() if r['status'] == 'error')
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.results.items():
            status_emoji = "✅" if result['status'] == 'success' else ("❌" if result['status'] == 'failed' else "⚠️")
            print(f"{status_emoji} {test_name}: {result['status']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results.json")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()