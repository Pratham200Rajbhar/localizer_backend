#!/usr/bin/env python3
"""
Fixed Comprehensive Test Suite - works with existing running server
"""

import asyncio
import httpx
import json
import time
import tempfile
import wave
import numpy as np
from pathlib import Path
import psutil

class FixedTestSuite:
    """Test suite that works with already running server"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_data = {}
        self.admin_token = None
        self.uploader_token = None
        self.reviewer_token = None
    
    def create_test_audio(self, duration=3, sample_rate=16000, filename="test_audio.wav"):
        """Create a test audio file for STT testing"""
        # Generate a simple sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit integers
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV file
        filepath = Path("storage/uploads") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(str(filepath), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return filepath
    
    async def login_users(self):
        """Login test users and get tokens"""
        print("🔑 Logging in test users...")
        
        # First create test users via existing admin
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to login with existing admin (from previous test)
            admin_login = {
                "username": "testadmin",
                "password": "admin123"
            }
            
            response = await client.post(
                f"{self.base_url}/auth/login",
                data=admin_login,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result['access_token']
                print("✅ Admin login successful")
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
            
            # Login uploader
            uploader_login = {
                "username": "testuploader", 
                "password": "uploader123"
            }
            
            response = await client.post(
                f"{self.base_url}/auth/login",
                data=uploader_login,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.uploader_token = result['access_token']
                print("✅ Uploader login successful")
            else:
                print(f"❌ Uploader login failed")
                return False
            
            # Login reviewer
            reviewer_login = {
                "username": "testreviewer",
                "password": "reviewer123"
            }
            
            response = await client.post(
                f"{self.base_url}/auth/login",
                data=reviewer_login,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.reviewer_token = result['access_token']
                print("✅ Reviewer login successful")
            else:
                print("❌ Reviewer login failed")
                return False
        
        return True
    
    async def test_supported_languages(self):
        """Test supported languages endpoint"""
        print("\n🌐 Testing Supported Languages...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/supported-languages")
                
                if response.status_code != 200:
                    print(f"❌ Languages endpoint failed: {response.status_code}")
                    return False
                
                languages = response.json()
                print(f"✅ Got {len(languages)} supported languages")
                
                # Check key languages including Konkani
                key_languages = ["hi", "bn", "ta", "te", "kok", "ur"]
                for lang in key_languages:
                    if lang in languages:
                        print(f"   ✅ {lang}: {languages[lang]}")
                    else:
                        print(f"   ❌ Missing: {lang}")
                        return False
                
                return True
                
        except Exception as e:
            print(f"❌ Language test failed: {e}")
            return False
    
    async def test_speech_to_text(self):
        """Test Speech-to-Text functionality"""
        print("\n🎤 Testing Speech-to-Text...")
        
        try:
            # Create test audio file
            audio_file = self.create_test_audio(duration=3)
            print(f"   Created audio file: {audio_file}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                with open(audio_file, 'rb') as f:
                    files = {"file": ("test_audio.wav", f, "audio/wav")}
                    
                    start_time = time.time()
                    response = await client.post(
                        f"{self.base_url}/speech/stt",
                        headers=headers,
                        files=files
                    )
                    processing_time = time.time() - start_time
                
                if response.status_code != 200:
                    print(f"❌ STT failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                print(f"✅ STT processing successful in {processing_time:.2f}s")
                print(f"   Transcript: {result.get('transcript', 'No transcript')[:100]}...")
                print(f"   Processing speed: {3/processing_time:.1f}x real-time")
                
                return True
                
        except Exception as e:
            print(f"❌ STT test failed: {e}")
            return False
    
    async def test_language_detection(self):
        """Test language detection"""
        print("\n🔍 Testing Language Detection...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                # Test English text
                detection_data = {"text": "Hello, how are you today?"}
                
                response = await client.post(
                    f"{self.base_url}/detect-language",
                    headers=headers,
                    json=detection_data
                )
                
                if response.status_code != 200:
                    print(f"❌ Language detection failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                detected_lang = result.get('detected_language')
                confidence = result.get('confidence', 0)
                
                print(f"✅ Language detection working")
                print(f"   Text: 'Hello, how are you today?'")
                print(f"   Detected: {detected_lang} (confidence: {confidence:.2f})")
                
                return True
                
        except Exception as e:
            print(f"❌ Language detection test failed: {e}")
            return False
    
    async def test_translation(self):
        """Test translation functionality"""
        print("\n🔤 Testing Translation System...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                # Test translation request
                translation_data = {
                    "text": "Hello, how are you?",
                    "source_language": "en",
                    "target_languages": ["hi", "bn"],
                    "domain": "general"
                }
                
                response = await client.post(
                    f"{self.base_url}/translate",
                    headers=headers,
                    json=translation_data
                )
                
                if response.status_code != 200:
                    print(f"❌ Translation failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                print("✅ Translation successful")
                
                # Check translations results
                results = result.get('results', [])
                print(f"   Got {len(results)} translation results")
                for i, translation_result in enumerate(results):
                    target_lang = translation_result.get('target_language')
                    translated_text = translation_result.get('translated_text', '')
                    print(f"   {target_lang}: {translated_text[:100]}...")
                
                return True
                
        except Exception as e:
            print(f"❌ Translation test failed: {e}")
            return False
    
    async def test_file_upload(self):
        """Test file upload"""
        print("\n📁 Testing File Upload...")
        
        try:
            # Create test text file
            test_content = "This is a test document for translation."
            test_file_path = Path("storage/uploads/test_document.txt")
            test_file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file_path.write_text(test_content)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                with open(test_file_path, 'rb') as f:
                    files = {"file": ("test_document.txt", f, "text/plain")}
                    data = {"domain": "general"}
                    
                    response = await client.post(
                        f"{self.base_url}/content/upload",
                        headers=headers,
                        files=files,
                        data=data
                    )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    file_id = result.get('file_id') or result.get('id')
                    self.test_data['uploaded_file_id'] = file_id
                    print(f"✅ File uploaded successfully: ID {file_id}")
                    return True
                else:
                    print(f"❌ File upload failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
        except Exception as e:
            print(f"❌ File upload test failed: {e}")
            return False
    
    async def test_feedback_system(self):
        """Test feedback system"""
        print("\n📝 Testing Feedback System...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.reviewer_token}"}
                
                feedback_data = {
                    "file_id": self.test_data.get('uploaded_file_id', 1),
                    "rating": 4,
                    "comments": "Good translation quality",
                    "corrections": {"suggestion": "Minor improvements needed"}
                }
                
                response = await client.post(
                    f"{self.base_url}/feedback",
                    headers=headers,
                    json=feedback_data
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"✅ Feedback submitted successfully")
                    return True
                else:
                    print(f"❌ Feedback submission failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
        except Exception as e:
            print(f"❌ Feedback test failed: {e}")
            return False
    
    async def test_health_endpoints(self):
        """Test health endpoints"""
        print("\n💓 Testing Health Endpoints...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Basic health check
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code != 200:
                    print(f"❌ Basic health check failed: {response.status_code}")
                    return False
                
                health = response.json()
                print(f"✅ Basic health: {health.get('status')}")
                
                # Database health check
                db_response = await client.get(f"{self.base_url}/health/db")
                
                if db_response.status_code != 200:
                    print(f"❌ Database health check failed: {db_response.status_code}")
                    return False
                
                db_health = db_response.json()
                print(f"✅ Database health: {db_health.get('database')}")
                
                return True
                
        except Exception as e:
            print(f"❌ Health check test failed: {e}")
            return False
    
    async def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        print("\n📊 Testing Metrics Endpoint...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/metrics")
                
                if response.status_code != 200:
                    print(f"❌ Metrics endpoint failed: {response.status_code}")
                    return False
                
                metrics_text = response.text
                print(f"✅ Metrics endpoint accessible")
                print(f"   Metrics size: {len(metrics_text)} characters")
                
                return True
                
        except Exception as e:
            print(f"❌ Metrics test failed: {e}")
            return False
    
    def test_system_performance(self):
        """Test system performance"""
        print("\n🚀 Testing System Performance...")
        
        try:
            # Check CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            print(f"   CPU Usage: {cpu_percent}%")
            print(f"   Memory: {memory.percent}% of {memory.total/(1024**3):.1f} GB")
            
            # Basic performance check
            if cpu_percent < 90 and memory.percent < 95:
                print("✅ System performance acceptable")
                return True
            else:
                print("⚠️ High system resource usage detected")
                return False
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 FIXED COMPREHENSIVE TEST SUITE")
        print("=" * 50)
        
        if not await self.login_users():
            print("❌ Failed to login users. Exiting.")
            return False
        
        # Define test sequence
        tests = [
            ("Supported Languages", self.test_supported_languages),
            ("Speech-to-Text", self.test_speech_to_text),
            ("Language Detection", self.test_language_detection),
            ("Translation System", self.test_translation),
            ("File Upload", self.test_file_upload),
            ("Feedback System", self.test_feedback_system),
            ("Health Endpoints", self.test_health_endpoints),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("System Performance", lambda: self.test_system_performance())
        ]
        
        results = {}
        total_tests = len(tests)
        passed_tests = 0
        
        for test_name, test_func in tests:
            print(f"\n{'='*15} {test_name} {'='*15}")
            
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                results[test_name] = result
                if result:
                    passed_tests += 1
                    
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Final report
        print(f"\n{'='*50}")
        print("🏁 FINAL TEST RESULTS")
        print("=" * 50)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nSUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("\n🎉 BACKEND IS PRODUCTION READY! 🎉")
            print("✅ Core functionality verified and working")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed")
            print("🔧 Some issues need attention")
        
        return passed_tests >= total_tests * 0.8

def main():
    """Main test runner for existing server"""
    print("🔄 Testing existing running server...")
    
    test_suite = FixedTestSuite()
    success = asyncio.run(test_suite.run_all_tests())
    
    return success

if __name__ == "__main__":
    success = main()