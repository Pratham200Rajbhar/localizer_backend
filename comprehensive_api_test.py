#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE API ENDPOINT TEST SUITE
Complete end-to-end testing of all API endpoints with error handling and validation
"""

import requests
import json
import os
import time
import tempfile
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_AUDIO = "test_src/bhoomika-j.mp3"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class APITester:
    def __init__(self):
        self.token: Optional[str] = None
        self.test_results: List[Dict] = []
        self.translation_id: Optional[int] = None
        self.file_id: Optional[int] = None
        
    def log_test(self, category: str, test_name: str, success: bool, message: str = "", duration: float = 0):
        """Log test result"""
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        
        self.test_results.append({
            'category': category,
            'test': test_name,
            'success': success,
            'message': message,
            'duration': duration
        })
        
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        print(f"  {status} {test_name}{duration_str}")
        if message and not success:
            print(f"    {Colors.YELLOW}└─ {message}{Colors.END}")
    
    def print_category(self, category: str):
        """Print category header"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}🔧 {category.upper()}{Colors.END}")
        print("=" * 60)
    
    def print_summary(self):
        """Print final test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}📊 COMPREHENSIVE TEST SUMMARY{Colors.END}")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed_tests}{Colors.END}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ FAILED TESTS:{Colors.END}")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['category']}: {result['test']} - {result['message']}")
        
        overall_status = "🎉 ALL TESTS PASSED" if failed_tests == 0 else f"⚠️  {failed_tests} TESTS FAILED"
        print(f"\n{Colors.BOLD}{overall_status}{Colors.END}")
    
    # ==================== AUTHENTICATION TESTS ====================
    
    def test_authentication(self):
        """Test authentication endpoints"""
        self.print_category("Authentication")
        
        # Test login with correct credentials
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.log_test("Authentication", "Valid Login", True, duration=duration)
                else:
                    self.log_test("Authentication", "Valid Login", False, "No access token in response")
            else:
                self.log_test("Authentication", "Valid Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Authentication", "Valid Login", False, str(e))
        
        # Test login with invalid credentials
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                data={"username": "admin", "password": "wrongpassword"}
            )
            duration = time.time() - start_time
            
            success = response.status_code == 401
            self.log_test("Authentication", "Invalid Login Rejection", success, 
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Authentication", "Invalid Login Rejection", False, str(e))
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    # ==================== HEALTH & STATUS TESTS ====================
    
    def test_health_status(self):
        """Test health and status endpoints"""
        self.print_category("Health & Status")
        
        # Test health endpoint
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("status") == "healthy"
                self.log_test("Health", "Health Check", success, 
                             f"Status: {data.get('status')}" if not success else "", duration)
            else:
                self.log_test("Health", "Health Check", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health", "Health Check", False, str(e))
        
        # Test supported languages
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/supported-languages", headers=self.get_headers())
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                languages = data.get("languages", {})
                success = len(languages) >= 22
                self.log_test("Health", "Supported Languages", success, 
                             f"Found {len(languages)} languages" if success else f"Found only {len(languages)} languages", duration)
            else:
                self.log_test("Health", "Supported Languages", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Health", "Supported Languages", False, str(e))
    
    # ==================== LANGUAGE DETECTION TESTS ====================
    
    def test_language_detection(self):
        """Test language detection endpoint"""
        self.print_category("Language Detection")
        
        test_cases = [
            ("Hello world", "en", "English text"),
            ("नमस्ते दुनिया", "hi", "Hindi text"),
            ("হ্যালো বিশ্ব", "bn", "Bengali text"),
        ]
        
        for text, expected_lang, description in test_cases:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{BASE_URL}/detect-language",
                    params={"text": text},
                    headers=self.get_headers()
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    detected = data.get("detected_language")
                    success = detected == expected_lang
                    self.log_test("Language Detection", description, success,
                                 f"Expected {expected_lang}, got {detected}" if not success else "", duration)
                else:
                    self.log_test("Language Detection", description, False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Language Detection", description, False, str(e))
    
    # ==================== TRANSLATION TESTS ====================
    
    def test_translation(self):
        """Test translation endpoints"""
        self.print_category("Translation")
        
        # Test valid translation
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={
                    "text": "Hello world",
                    "source_language": "en",
                    "target_languages": ["hi"]
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    result = data["results"][0]
                    translated_text = result.get("translated_text", "")
                    self.translation_id = result.get("translation_id")
                    
                    success = len(translated_text.strip()) > 0
                    self.log_test("Translation", "English to Hindi", success,
                                 f"Got: '{translated_text}'" if success else "Empty translation", duration)
                else:
                    self.log_test("Translation", "English to Hindi", False, "No results returned")
            else:
                self.log_test("Translation", "English to Hindi", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Translation", "English to Hindi", False, str(e))
        
        # Test invalid source language
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={
                    "text": "Hello world",
                    "source_language": "xyz",
                    "target_languages": ["hi"]
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            success = response.status_code == 422
            self.log_test("Translation", "Invalid Source Language", success,
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Translation", "Invalid Source Language", False, str(e))
        
        # Test multiple target languages
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={
                    "text": "Good morning",
                    "source_language": "en",
                    "target_languages": ["hi", "ta", "bn"]
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                success = len(results) == 3
                self.log_test("Translation", "Multiple Target Languages", success,
                             f"Expected 3 results, got {len(results)}" if not success else "", duration)
            else:
                self.log_test("Translation", "Multiple Target Languages", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Translation", "Multiple Target Languages", False, str(e))
    
    # ==================== SPEECH PROCESSING TESTS ====================
    
    def test_speech_processing(self):
        """Test speech-to-text and text-to-speech endpoints"""
        self.print_category("Speech Processing")
        
        # Test STT if audio file exists
        if os.path.exists(TEST_AUDIO):
            start_time = time.time()
            try:
                with open(TEST_AUDIO, 'rb') as f:
                    response = requests.post(
                        f"{BASE_URL}/speech/stt",
                        files={'file': ('audio.mp3', f, 'audio/mpeg')},
                        headers=self.get_headers()
                    )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    transcript = data.get("transcript", "")
                    success = len(transcript.strip()) > 0
                    self.log_test("Speech", "Speech-to-Text", success,
                                 f"Transcript length: {len(transcript)}" if success else "Empty transcript", duration)
                else:
                    self.log_test("Speech", "Speech-to-Text", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Speech", "Speech-to-Text", False, str(e))
        else:
            self.log_test("Speech", "Speech-to-Text", False, f"Audio file not found: {TEST_AUDIO}")
        
        # Test TTS
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/speech/tts",
                json={
                    "text": "नमस्ते दुनिया",
                    "language": "hi",
                    "voice": "female"
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                audio_path = data.get("audio_path", "")
                success = len(audio_path) > 0
                self.log_test("Speech", "Text-to-Speech", success,
                             f"Audio path: {audio_path}" if success else "No audio path", duration)
            else:
                self.log_test("Speech", "Text-to-Speech", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Speech", "Text-to-Speech", False, str(e))
        
        # Test TTS with invalid language
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/speech/tts",
                json={
                    "text": "Hello world",
                    "language": "xyz",
                    "voice": "female"
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            success = response.status_code == 422
            self.log_test("Speech", "TTS Invalid Language", success,
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Speech", "TTS Invalid Language", False, str(e))
    
    # ==================== EVALUATION TESTS ====================
    
    def test_evaluation(self):
        """Test evaluation endpoints"""
        self.print_category("Evaluation")
        
        if not self.translation_id:
            self.log_test("Evaluation", "Translation Evaluation", False, "No translation_id available")
            return
        
        # Test evaluation
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/evaluate/run",
                json={
                    "translation_id": self.translation_id,
                    "reference_text": "नमस्ते संसार"
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = "bleu_score" in data and "comet_score" in data
                self.log_test("Evaluation", "Translation Evaluation", success,
                             f"BLEU: {data.get('bleu_score')}, COMET: {data.get('comet_score')}" if success else "Missing scores", duration)
            else:
                self.log_test("Evaluation", "Translation Evaluation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Evaluation", "Translation Evaluation", False, str(e))
        
        # Test evaluation with invalid translation_id
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/evaluate/run",
                json={
                    "translation_id": 99999,
                    "reference_text": "Test reference"
                },
                headers=self.get_headers()
            )
            duration = time.time() - start_time
            
            success = response.status_code == 404
            self.log_test("Evaluation", "Invalid Translation ID", success,
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Evaluation", "Invalid Translation ID", False, str(e))
    
    # ==================== FEEDBACK TESTS ====================
    
    def test_feedback(self):
        """Test feedback endpoints"""
        self.print_category("Feedback")
        
        # Test get feedback (should work even if empty)
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/feedback", headers=self.get_headers())
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = isinstance(data, list)
                self.log_test("Feedback", "Get Feedback List", success,
                             f"Found {len(data)} feedback items" if success else "Invalid response format", duration)
            else:
                self.log_test("Feedback", "Get Feedback List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Feedback", "Get Feedback List", False, str(e))
        
        # Test submit feedback (if we have a translation_id)
        if self.translation_id:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{BASE_URL}/feedback",
                    json={
                        "translation_id": self.translation_id,
                        "rating": 4,
                        "comments": "Test feedback comment",
                        "corrections": {"suggested": "Better translation"}
                    },
                    headers=self.get_headers()
                )
                duration = time.time() - start_time
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    success = "id" in data and data.get("rating") == 4
                    self.log_test("Feedback", "Submit Feedback", success,
                                 f"Feedback ID: {data.get('id')}" if success else "Invalid response", duration)
                else:
                    self.log_test("Feedback", "Submit Feedback", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Feedback", "Submit Feedback", False, str(e))
    
    # ==================== FILE MANAGEMENT TESTS ====================
    
    def test_file_management(self):
        """Test file upload and management endpoints"""
        self.print_category("File Management")
        
        # Test get user files
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/content/files", headers=self.get_headers())
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = isinstance(data, list)
                self.log_test("File Management", "Get User Files", success,
                             f"Found {len(data)} files" if success else "Invalid response format", duration)
            else:
                self.log_test("File Management", "Get User Files", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("File Management", "Get User Files", False, str(e))
        
        # Test file upload with a temporary file
        start_time = time.time()
        try:
            # Create a temporary text file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write("This is a test document for upload testing.")
                temp_file_path = temp_file.name
            
            with open(temp_file_path, 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/content/upload",
                    files={'file': ('test_document.txt', f, 'text/plain')},
                    data={'domain': 'general', 'source_language': 'en'},
                    headers=self.get_headers()
                )
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.file_id = data.get("id")
                success = "id" in data and "filename" in data
                self.log_test("File Management", "File Upload", success,
                             f"File ID: {data.get('id')}" if success else "Invalid response", duration)
            else:
                self.log_test("File Management", "File Upload", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("File Management", "File Upload", False, str(e))
    
    # ==================== ERROR HANDLING TESTS ====================
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        self.print_category("Error Handling")
        
        # Test unauthorized access (using translate endpoint which requires auth)
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={"text": "test", "source_language": "en", "target_languages": ["hi"]}
            )  # No auth header
            duration = time.time() - start_time
            
            success = response.status_code == 401
            self.log_test("Error Handling", "Unauthorized Access", success,
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Error Handling", "Unauthorized Access", False, str(e))
        
        # Test malformed JSON
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                data="invalid json",
                headers={**self.get_headers(), "Content-Type": "application/json"}
            )
            duration = time.time() - start_time
            
            success = response.status_code in [400, 422]
            self.log_test("Error Handling", "Malformed JSON", success,
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Error Handling", "Malformed JSON", False, str(e))
        
        # Test non-existent endpoint
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/nonexistent", headers=self.get_headers())
            duration = time.time() - start_time
            
            success = response.status_code == 404
            self.log_test("Error Handling", "Non-existent Endpoint", success,
                         f"Status: {response.status_code}" if not success else "", duration)
        except Exception as e:
            self.log_test("Error Handling", "Non-existent Endpoint", False, str(e))
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"{Colors.CYAN}{Colors.BOLD}🧪 COMPREHENSIVE API ENDPOINT TEST SUITE{Colors.END}")
        print(f"{Colors.CYAN}Starting comprehensive testing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print("=" * 60)
        
        # Run all test suites
        self.test_authentication()
        
        if not self.token:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ AUTHENTICATION FAILED - ABORTING TESTS{Colors.END}")
            return
        
        self.test_health_status()
        self.test_language_detection()
        self.test_translation()
        self.test_speech_processing()
        self.test_evaluation()
        self.test_feedback()
        self.test_file_management()
        self.test_error_handling()
        
        # Print final summary
        self.print_summary()

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()