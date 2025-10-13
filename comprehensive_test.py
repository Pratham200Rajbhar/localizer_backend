#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TEST SUITE
Tests all components according to master prompt specifications
"""

import asyncio
import httpx
import json
import sys
import os
import time
import tempfile
import wave
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
import pytest
import psutil

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.core.db import get_db, engine, Base
from app.models.user import User
from app.models.file import File
from app.models.translation import Translation
from app.models.feedback import Feedback
from sqlalchemy.orm import sessionmaker

settings = get_settings()

class ComprehensiveTestSuite:
    """Complete test suite for the backend system"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"  # Use different port to avoid conflicts
        self.test_data = {}
        self.admin_token = None
        self.uploader_token = None
        self.reviewer_token = None
        
    async def setup_database(self):
        """Setup test database and users"""
        print("🔧 Setting up test database...")
        
        try:
            # Create tables
            Base.metadata.create_all(bind=engine)
            
            # Create session
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            # Clean up existing test users
            db.query(User).filter(User.username.in_(['testadmin', 'testuploader', 'testreviewer'])).delete(synchronize_session=False)
            db.commit()
            
            # Create test users
            test_users = [
                User(username="testadmin", password="admin123", role="admin"),
                User(username="testuploader", password="uploader123", role="uploader"),
                User(username="testreviewer", password="reviewer123", role="reviewer")
            ]
            
            for user in test_users:
                db.add(user)
            
            db.commit()
            db.close()
            
            print("✅ Test database setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    def create_test_audio(self, duration=5, sample_rate=16000, filename="test_audio.wav"):
        """Create a test audio file for STT testing"""
        print(f"🎵 Creating test audio file: {filename}")
        
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
    
    async def test_authentication(self):
        """Test authentication system with plain text passwords"""
        print("\n🔐 Testing Authentication System...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test login for each user type
                users_to_test = [
                    ("testadmin", "admin123", "admin"),
                    ("testuploader", "uploader123", "uploader"),
                    ("testreviewer", "reviewer123", "reviewer")
                ]
                
                for username, password, role in users_to_test:
                    print(f"  Testing login for {role}: {username}")
                    
                    login_data = {
                        "username": username,
                        "password": password
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/auth/login",
                        data=login_data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Login failed for {username}: {response.status_code}")
                        print(f"   Response: {response.text}")
                        return False
                    
                    result = response.json()
                    token = result['access_token']
                    
                    # Store tokens for later use
                    if role == "admin":
                        self.admin_token = token
                    elif role == "uploader":
                        self.uploader_token = token
                    elif role == "reviewer":
                        self.reviewer_token = token
                    
                    print(f"✅ Login successful for {username} ({role})")
                    
                    # Test protected endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = await client.get(f"{self.base_url}/auth/me", headers=headers)
                    
                    if me_response.status_code != 200:
                        print(f"❌ Protected endpoint failed for {username}")
                        return False
                    
                    user_info = me_response.json()
                    print(f"   User info: {user_info['username']} ({user_info['role']})")
                
                print("✅ Authentication tests passed")
                return True
                
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False
    
    async def test_supported_languages(self):
        """Test supported languages endpoint and validation"""
        print("\n🌐 Testing Supported Languages...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/supported-languages")
                
                if response.status_code != 200:
                    print(f"❌ Languages endpoint failed: {response.status_code}")
                    return False
                
                languages = response.json()
                print(f"✅ Got {len(languages)} supported languages")
                
                # Verify all 22 Indian languages are present
                expected_languages = set(SUPPORTED_LANGUAGES.keys())
                received_languages = set(languages.keys())
                
                if expected_languages != received_languages:
                    missing = expected_languages - received_languages
                    extra = received_languages - expected_languages
                    
                    if missing:
                        print(f"❌ Missing languages: {missing}")
                    if extra:
                        print(f"❌ Extra languages: {extra}")
                    return False
                
                # Verify specific languages including Konkani
                key_languages = ["hi", "bn", "ta", "te", "kok", "ur"]
                for lang in key_languages:
                    if lang not in languages:
                        print(f"❌ Key language missing: {lang}")
                        return False
                    print(f"   {lang}: {languages[lang]}")
                
                print("✅ All 22 Indian languages supported correctly")
                return True
                
        except Exception as e:
            print(f"❌ Language test failed: {e}")
            return False
    
    async def test_file_upload(self):
        """Test file upload functionality"""
        print("\n📁 Testing File Upload...")
        
        try:
            # Create test text file
            test_content = "This is a test document for translation. It contains multiple sentences."
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
                
                if response.status_code not in [200, 201]:
                    print(f"❌ File upload failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                self.test_data['uploaded_file_id'] = result.get('file_id')
                print(f"✅ File uploaded successfully: ID {result.get('file_id')}")
                return True
                
        except Exception as e:
            print(f"❌ File upload test failed: {e}")
            return False
    
    async def test_speech_to_text(self):
        """Test Speech-to-Text functionality"""
        print("\n🎤 Testing Speech-to-Text...")
        
        try:
            # Create test audio file
            audio_file = self.create_test_audio(duration=3)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                with open(audio_file, 'rb') as f:
                    # files = {"file": ("E:\\new_backend\\demo.mp3", f, "audio/wav")}
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
                print(f"   Transcript: {result.get('transcript', 'No transcript')}")
                print(f"   Processing speed: {3/processing_time:.1f}x real-time")
                
                # Verify performance is acceptable (should be faster than real-time)
                if processing_time > 3:
                    print(f"⚠️ STT processing slower than real-time")
                
                return True
                
        except Exception as e:
            print(f"❌ STT test failed: {e}")
            return False
    
    async def test_translation(self):
        """Test translation functionality"""
        print("\n🔤 Testing Translation System...")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                # Test translation request
                translation_data = {
                    "text": "Hello, how are you? This is a test message for translation.",
                    "source_language": "en",
                    "target_languages": ["hi", "bn", "ta"],
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
                
                # Verify translations for each target language
                translations = result.get('translations', {})
                for lang in ["hi", "bn", "ta"]:
                    if lang in translations:
                        translation_text = translations[lang].get('text', '')
                        print(f"   {lang}: {translation_text[:50]}...")
                    else:
                        print(f"❌ Missing translation for {lang}")
                        return False
                
                self.test_data['translation_result'] = result
                return True
                
        except Exception as e:
            print(f"❌ Translation test failed: {e}")
            return False
    
    async def test_language_detection(self):
        """Test language detection"""
        print("\n🔍 Testing Language Detection...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.uploader_token}"}
                
                # Test texts in different languages
                test_texts = [
                    ("Hello, how are you today?", "en"),
                    ("नमस्ते, आप कैसे हैं?", "hi"),
                    ("আপনি কেমন আছেন?", "bn"),
                    ("நீங்கள் எப்படி இருக்கிறீர்கள்?", "ta")
                ]
                
                for text, expected_lang in test_texts:
                    detection_data = {"text": text}
                    
                    response = await client.post(
                        f"{self.base_url}/detect-language",
                        headers=headers,
                        json=detection_data
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Language detection failed for {expected_lang}: {response.status_code}")
                        continue
                    
                    result = response.json()
                    detected_lang = result.get('detected_language')
                    confidence = result.get('confidence', 0)
                    
                    print(f"   Text: {text[:30]}...")
                    print(f"   Detected: {detected_lang} (confidence: {confidence:.2f})")
                    
                    if detected_lang == expected_lang:
                        print(f"✅ Correct detection for {expected_lang}")
                    else:
                        print(f"⚠️ Expected {expected_lang}, got {detected_lang}")
                
                return True
                
        except Exception as e:
            print(f"❌ Language detection test failed: {e}")
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
                    "comments": "Good translation quality overall",
                    "corrections": "Minor grammar improvements needed"
                }
                
                response = await client.post(
                    f"{self.base_url}/feedback",
                    headers=headers,
                    json=feedback_data
                )
                
                if response.status_code not in [200, 201]:
                    print(f"❌ Feedback submission failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                print(f"✅ Feedback submitted successfully: ID {result.get('id')}")
                return True
                
        except Exception as e:
            print(f"❌ Feedback test failed: {e}")
            return False
    
    async def test_job_management(self):
        """Test job management and retraining"""
        print("\n⚙️ Testing Job Management...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                # Test job listing
                response = await client.get(f"{self.base_url}/jobs", headers=headers)
                
                if response.status_code != 200:
                    print(f"❌ Job listing failed: {response.status_code}")
                    return False
                
                jobs = response.json()
                print(f"✅ Job listing successful: {jobs.get('total', 0)} active jobs")
                
                # Test retraining trigger (admin only)
                retrain_data = {
                    "domain": "general",
                    "model_type": "indicTrans2",
                    "epochs": 1,  # Small number for testing
                    "batch_size": 8
                }
                
                response = await client.post(
                    f"{self.base_url}/jobs/retrain",
                    headers=headers,
                    params=retrain_data
                )
                
                if response.status_code != 200:
                    print(f"❌ Retraining trigger failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                job_id = result.get('job_id')
                print(f"✅ Retraining job triggered: {job_id}")
                
                # Check job status
                if job_id:
                    await asyncio.sleep(2)  # Wait a bit
                    status_response = await client.get(f"{self.base_url}/jobs/{job_id}", headers=headers)
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        print(f"   Job status: {status.get('status')}")
                        print(f"   Progress: {status.get('progress', 0)}%")
                
                return True
                
        except Exception as e:
            print(f"❌ Job management test failed: {e}")
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
                
                # Metrics should be in Prometheus format
                metrics_text = response.text
                print(f"✅ Metrics endpoint accessible")
                print(f"   Metrics length: {len(metrics_text)} characters")
                
                # Check for key metrics
                key_metrics = ['http_requests_total', 'request_duration_seconds', 'python_info']
                for metric in key_metrics:
                    if metric in metrics_text:
                        print(f"   ✅ Found metric: {metric}")
                    else:
                        print(f"   ⚠️ Missing metric: {metric}")
                
                return True
                
        except Exception as e:
            print(f"❌ Metrics test failed: {e}")
            return False
    
    async def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n💓 Testing Health Endpoints...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Basic health check
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code != 200:
                    print(f"❌ Basic health check failed: {response.status_code}")
                    return False
                
                health = response.json()
                print(f"✅ Basic health check: {health.get('status')}")
                
                # Database health check
                db_response = await client.get(f"{self.base_url}/health/db")
                
                if db_response.status_code != 200:
                    print(f"❌ Database health check failed: {db_response.status_code}")
                    return False
                
                db_health = db_response.json()
                print(f"✅ Database health: {db_health.get('database')}")
                
                # Detailed health check
                detailed_response = await client.get(f"{self.base_url}/health/detailed")
                
                if detailed_response.status_code != 200:
                    print(f"❌ Detailed health check failed: {detailed_response.status_code}")
                    return False
                
                detailed_health = detailed_response.json()
                print(f"✅ Detailed health check passed")
                
                # Check system info
                if 'system' in detailed_health:
                    system_info = detailed_health['system']
                    print(f"   CPU cores: {system_info.get('cpu_cores')}")
                    print(f"   Memory: {system_info.get('memory_gb', 0):.1f} GB")
                
                return True
                
        except Exception as e:
            print(f"❌ Health check test failed: {e}")
            return False
    
    def test_system_performance(self):
        """Test system performance and resource usage"""
        print("\n🚀 Testing System Performance...")
        
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"   CPU Usage: {cpu_percent}%")
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_used_percent = memory.percent
            print(f"   Memory: {memory_used_percent}% of {memory_gb:.1f} GB")
            
            # Check disk usage
            disk = psutil.disk_usage('.')
            disk_gb = disk.total / (1024**3)
            disk_used_percent = (disk.used / disk.total) * 100
            print(f"   Disk: {disk_used_percent:.1f}% of {disk_gb:.1f} GB")
            
            # Performance thresholds
            performance_issues = []
            
            if cpu_percent > 80:
                performance_issues.append("High CPU usage")
            
            if memory_used_percent > 85:
                performance_issues.append("High memory usage")
            
            if disk_used_percent > 90:
                performance_issues.append("High disk usage")
            
            if performance_issues:
                print(f"⚠️ Performance issues detected: {', '.join(performance_issues)}")
            else:
                print("✅ System performance within acceptable limits")
            
            return len(performance_issues) == 0
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 COMPREHENSIVE BACKEND TEST SUITE")
        print("=" * 60)
        
        # Setup
        if not await self.setup_database():
            return False
        
        # Define test sequence
        tests = [
            ("Authentication", self.test_authentication),
            ("Supported Languages", self.test_supported_languages),
            ("File Upload", self.test_file_upload),
            ("Speech-to-Text", self.test_speech_to_text),
            ("Translation System", self.test_translation),
            ("Language Detection", self.test_language_detection),
            ("Feedback System", self.test_feedback_system),
            ("Job Management", self.test_job_management),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("Health Endpoints", self.test_health_endpoints),
            ("System Performance", lambda: self.test_system_performance())
        ]
        
        results = {}
        total_tests = len(tests)
        passed_tests = 0
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
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
        print("\n" + "="*60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Backend is ready for production! 🎉")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed. Issues need to be fixed.")
        
        return passed_tests == total_tests

def main():
    """Main test runner"""
    import subprocess
    import time
    
    print("🚀 Starting FastAPI server for testing...")
    
    # Start server in background
    server_process = None
    try:
        server_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8001"],
            cwd=str(Path(__file__).parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Run tests
        test_suite = ComprehensiveTestSuite()
        success = asyncio.run(test_suite.run_all_tests())
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return False
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False
        
    finally:
        if server_process:
            print("\n🛑 Stopping test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)