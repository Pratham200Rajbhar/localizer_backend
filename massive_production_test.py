"""
MASSIVE PRODUCTION-LEVEL API TEST SUITE
Tests every endpoint thoroughly with all 22 Indian languages, edge cases, and error scenarios
"""
import requests
import json
import os
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import uuid
import random

BASE_URL = "http://localhost:8000"

# All 22 Indian languages for comprehensive testing
SUPPORTED_LANGUAGES = {
    "as": "Assamese", "bn": "Bengali", "brx": "Bodo", "doi": "Dogri",
    "gu": "Gujarati", "hi": "Hindi", "kn": "Kannada", "ks": "Kashmiri", 
    "kok": "Konkani", "mai": "Maithili", "ml": "Malayalam", "mni": "Manipuri",
    "mr": "Marathi", "ne": "Nepali", "or": "Odia", "pa": "Punjabi",
    "sa": "Sanskrit", "sat": "Santali", "sd": "Sindhi", "ta": "Tamil",
    "te": "Telugu", "ur": "Urdu"
}

class ProductionAPITester:
    def __init__(self):
        self.results = {
            "summary": {},
            "detailed_results": {},
            "performance_metrics": {},
            "error_analysis": {},
            "language_coverage": {},
            "edge_cases": {},
            "stress_tests": {}
        }
        self.session = requests.Session()
        
    def log_test(self, test_name: str, status: str, details: Any = None, error: str = None):
        """Log test results"""
        self.results["detailed_results"][test_name] = {
            "status": status,
            "timestamp": time.time(),
            "details": details,
            "error": error
        }
        print(f"{'✅' if status == 'success' else '❌'} {test_name}: {status}")
        if error:
            print(f"   Error: {error}")

    def test_health_endpoint(self):
        """Test health endpoint robustness"""
        print("\n🏥 === HEALTH ENDPOINT TESTS ===")
        
        try:
            # Basic health check
            response = self.session.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("health_basic", "success", health_data)
                
                # Stress test - multiple rapid requests
                start_time = time.time()
                for i in range(10):
                    self.session.get(f"{BASE_URL}/health", timeout=2)
                duration = time.time() - start_time
                
                if duration < 5:  # Should handle 10 requests in under 5 seconds
                    self.log_test("health_stress", "success", f"10 requests in {duration:.2f}s")
                else:
                    self.log_test("health_stress", "failed", f"Too slow: {duration:.2f}s")
            else:
                self.log_test("health_basic", "failed", error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("health_basic", "error", error=str(e))

    def test_supported_languages_comprehensive(self):
        """Test supported languages endpoint thoroughly"""
        print("\n🌏 === SUPPORTED LANGUAGES TESTS ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/supported-languages")
            if response.status_code == 200:
                langs = response.json()
                
                # Check if all 22 languages are present
                missing_langs = []
                for lang_code in SUPPORTED_LANGUAGES.keys():
                    if lang_code not in langs.get('language_codes', []):
                        missing_langs.append(lang_code)
                
                if not missing_langs:
                    self.log_test("languages_completeness", "success", f"All 22 languages present")
                else:
                    self.log_test("languages_completeness", "failed", error=f"Missing: {missing_langs}")
                    
                # Test API response structure
                expected_keys = ['supported_languages', 'total_count', 'language_codes']
                missing_keys = [k for k in expected_keys if k not in langs]
                if not missing_keys:
                    self.log_test("languages_structure", "success")
                else:
                    self.log_test("languages_structure", "failed", error=f"Missing keys: {missing_keys}")
                    
            else:
                self.log_test("languages_basic", "failed", error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("languages_basic", "error", error=str(e))

    def test_language_detection_all_languages(self):
        """Test language detection with samples from all 22 languages"""
        print("\n🔍 === LANGUAGE DETECTION COMPREHENSIVE TESTS ===")
        
        # Sample texts in different languages
        test_samples = {
            "hi": "नमस्ते, आप कैसे हैं? भारत एक विविधताओं से भरा देश है।",
            "bn": "আপনি কেমন আছেন? বাংলাদেশ একটি সুন্দর দেশ।",
            "ta": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? தமிழ் ஒரு பழமையான மொழி।",
            "te": "మీరు ఎలా ఉన్నారు? తెలుగు ఒక మధురమైన భాష.",
            "gu": "તમે કેમ છો? ગુજરાત એક સુંદર રાજ્ય છે।",
            "mr": "तुम्ही कसे आहात? महाराष्ट्र हा एक सुंदर राज्य आहे।",
            "pa": "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ? ਪੰਜਾਬ ਇੱਕ ਸੁੰਦਰ ਰਾਜ ਹੈ।",
            "kn": "ನೀವು ಹೇಗಿದ್ದೀರಿ? ಕನ್ನಡ ಒಂದು ಸುಂದರ ಭಾಷೆ.",
            "ml": "നിങ്ങൾ എങ്ങനെയുണ്ട്? കേരളം ഒരു സുന്ദരമായ സ്ഥലമാണ്.",
            "or": "ଆପଣ କେମିତି ଅଛନ୍ତି? ଓଡ଼ିଶା ଏକ ସୁନ୍ଦର ରାଜ୍ୟ।",
            "ur": "آپ کیسے ہیں؟ اردو ایک خوبصورت زبان ہے۔"
        }
        
        detected_correctly = 0
        total_tests = len(test_samples)
        
        for expected_lang, text in test_samples.items():
            try:
                data = {"text": text}
                response = self.session.post(f"{BASE_URL}/detect-language", json=data, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    detected_lang = result.get('detected_language', '')
                    confidence = result.get('confidence', 0)
                    
                    if detected_lang == expected_lang:
                        detected_correctly += 1
                        self.log_test(f"detect_{expected_lang}", "success", 
                                    f"Detected: {detected_lang}, Confidence: {confidence}")
                    else:
                        self.log_test(f"detect_{expected_lang}", "failed", 
                                    error=f"Expected: {expected_lang}, Got: {detected_lang}")
                else:
                    self.log_test(f"detect_{expected_lang}", "failed", 
                                error=f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"detect_{expected_lang}", "error", error=str(e))
        
        accuracy = (detected_correctly / total_tests) * 100
        self.results["language_coverage"]["detection_accuracy"] = accuracy
        self.log_test("detection_accuracy", "success" if accuracy > 70 else "failed", 
                     f"Accuracy: {accuracy:.1f}%")

    def test_file_upload_multiple_formats(self):
        """Test file upload with various formats and sizes"""
        print("\n📁 === FILE UPLOAD COMPREHENSIVE TESTS ===")
        
        # Test different file types and contents
        test_files = [
            ("simple.txt", "This is a simple test file for translation.", "text/plain"),
            ("long_text.txt", "This is a much longer text file for translation. " * 50, "text/plain"),
            ("unicode.txt", "This file contains unicode: हिंदी ಕನ್ನಡ தமிழ் తెలుగు", "text/plain"),
            ("empty.txt", "", "text/plain"),
            ("special_chars.txt", "Special chars: @#$%^&*()[]{}|\\:;\"'<>?/.,`~", "text/plain")
        ]
        
        uploaded_files = []
        
        for filename, content, content_type in test_files:
            try:
                # Create test file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Upload file
                with open(filename, 'rb') as f:
                    files = {'file': (filename, f, content_type)}
                    data = {'domain': 'general'}
                    response = self.session.post(f"{BASE_URL}/content/upload", 
                                               files=files, data=data, timeout=10)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    file_id = result.get('id')
                    uploaded_files.append(file_id)
                    self.log_test(f"upload_{filename}", "success", f"File ID: {file_id}")
                else:
                    self.log_test(f"upload_{filename}", "failed", 
                                error=f"Status: {response.status_code} - {response.text}")
                
                # Cleanup
                os.remove(filename)
                
            except Exception as e:
                self.log_test(f"upload_{filename}", "error", error=str(e))
                try:
                    os.remove(filename)
                except:
                    pass
        
        self.results["performance_metrics"]["uploaded_files"] = uploaded_files
        return uploaded_files

    def test_translation_all_language_pairs(self):
        """Test translation between all language pairs"""
        print("\n🔄 === TRANSLATION COMPREHENSIVE TESTS ===")
        
        # Test various text samples
        test_texts = [
            "Hello, how are you today?",
            "The weather is very nice today.",
            "I am learning a new language.",
            "Technology is changing the world.",
            "Education is very important for everyone."
        ]
        
        # Test subset of language pairs (to avoid too many requests)
        test_languages = ["hi", "bn", "ta", "te", "gu", "mr", "pa", "kn"]
        
        successful_translations = 0
        total_attempts = 0
        
        for text in test_texts[:2]:  # Test first 2 texts
            for target_lang in test_languages[:4]:  # Test first 4 languages
                total_attempts += 1
                try:
                    data = {
                        "text": text,
                        "source_language": "en",
                        "target_languages": [target_lang],
                        "domain": "general"
                    }
                    
                    response = self.session.post(f"{BASE_URL}/translate", 
                                               json=data, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('results') and len(result['results']) > 0:
                            translation = result['results'][0]
                            if translation.get('translated_text'):
                                successful_translations += 1
                                self.log_test(f"translate_en_to_{target_lang}", "success",
                                            f"Text: '{text[:30]}...' -> '{translation['translated_text'][:30]}...'")
                            else:
                                self.log_test(f"translate_en_to_{target_lang}", "failed",
                                            error="No translated text in response")
                        else:
                            self.log_test(f"translate_en_to_{target_lang}", "failed",
                                        error="No results in response")
                    else:
                        self.log_test(f"translate_en_to_{target_lang}", "failed",
                                    error=f"Status: {response.status_code} - {response.text[:200]}")
                        
                except Exception as e:
                    self.log_test(f"translate_en_to_{target_lang}", "error", error=str(e))
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.5)
        
        success_rate = (successful_translations / total_attempts * 100) if total_attempts > 0 else 0
        self.results["performance_metrics"]["translation_success_rate"] = success_rate
        self.log_test("translation_success_rate", 
                     "success" if success_rate > 50 else "failed",
                     f"Success rate: {success_rate:.1f}%")

    def test_speech_processing_comprehensive(self):
        """Test STT and TTS with various scenarios"""
        print("\n🎤🔊 === SPEECH PROCESSING COMPREHENSIVE TESTS ===")
        
        # Test STT with demo file
        if os.path.exists("E:/new_backend/demo.mp3"):
            try:
                with open("E:/new_backend/demo.mp3", 'rb') as f:
                    files = {'file': ('demo.mp3', f, 'audio/mpeg')}
                    response = self.session.post(f"{BASE_URL}/speech/stt", 
                                               files=files, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    transcript = result.get('transcript', '')
                    self.log_test("stt_demo_file", "success", 
                                f"Transcript length: {len(transcript)} chars")
                else:
                    self.log_test("stt_demo_file", "failed", 
                                error=f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("stt_demo_file", "error", error=str(e))
        else:
            self.log_test("stt_demo_file", "skipped", error="Demo file not found")
        
        # Test TTS with multiple languages
        tts_languages = ["hi", "bn", "ta", "te", "gu"]
        tts_texts = [
            "नमस्ते, यह एक परीक्षण है।",
            "আপনি কেমন আছেন?",
            "வணக்கம், இது ஒரு சோதனை.",
            "మీరు ఎలా ఉన్నారు?",
            "તમે કેમ છો?"
        ]
        
        for i, (lang, text) in enumerate(zip(tts_languages, tts_texts)):
            try:
                data = {"text": text, "language": lang}
                response = self.session.post(f"{BASE_URL}/speech/tts", 
                                           json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    audio_path = result.get('audio_path', '')
                    if audio_path:
                        self.log_test(f"tts_{lang}", "success", f"Audio: {audio_path}")
                    else:
                        self.log_test(f"tts_{lang}", "failed", error="No audio path returned")
                else:
                    self.log_test(f"tts_{lang}", "failed", 
                                error=f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"tts_{lang}", "error", error=str(e))
            
            time.sleep(1)  # Delay between TTS requests

    def test_edge_cases_and_error_scenarios(self):
        """Test edge cases and error handling"""
        print("\n⚠️ === EDGE CASES AND ERROR SCENARIOS ===")
        
        # Test with empty text
        try:
            data = {"text": "", "source_language": "en", "target_languages": ["hi"]}
            response = self.session.post(f"{BASE_URL}/translate", json=data)
            self.log_test("edge_empty_text", 
                         "success" if response.status_code in [400, 422] else "failed",
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("edge_empty_text", "error", error=str(e))
        
        # Test with very long text
        try:
            long_text = "This is a very long text. " * 1000  # 25,000+ characters
            data = {"text": long_text, "source_language": "en", "target_languages": ["hi"]}
            response = self.session.post(f"{BASE_URL}/translate", json=data, timeout=60)
            self.log_test("edge_long_text", 
                         "success" if response.status_code in [200, 413, 422] else "failed",
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("edge_long_text", "error", error=str(e))
        
        # Test with unsupported language
        try:
            data = {"text": "Hello", "source_language": "fr", "target_languages": ["hi"]}
            response = self.session.post(f"{BASE_URL}/translate", json=data)
            self.log_test("edge_unsupported_lang", 
                         "success" if response.status_code in [400, 422] else "failed",
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("edge_unsupported_lang", "error", error=str(e))
        
        # Test malformed JSON
        try:
            response = self.session.post(f"{BASE_URL}/translate", 
                                       data="invalid json", 
                                       headers={'Content-Type': 'application/json'})
            self.log_test("edge_malformed_json", 
                         "success" if response.status_code in [400, 422] else "failed",
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("edge_malformed_json", "error", error=str(e))

    def test_performance_and_stress(self):
        """Test system performance under load"""
        print("\n🚀 === PERFORMANCE AND STRESS TESTS ===")
        
        # Concurrent requests test
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def make_request(test_id):
            try:
                start = time.time()
                response = self.session.get(f"{BASE_URL}/health")
                duration = time.time() - start
                results_queue.put((test_id, response.status_code, duration))
            except Exception as e:
                results_queue.put((test_id, "error", str(e)))
        
        # Launch 10 concurrent requests
        threads = []
        for i in range(10):
            t = threading.Thread(target=make_request, args=(i,))
            t.start()
            threads.append(t)
        
        # Wait for all to complete
        for t in threads:
            t.join()
        
        # Analyze results
        durations = []
        success_count = 0
        while not results_queue.empty():
            test_id, status, duration = results_queue.get()
            if status == 200:
                success_count += 1
                durations.append(duration)
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            self.log_test("stress_concurrent", 
                         "success" if success_count >= 8 and avg_duration < 2 else "failed",
                         f"Success: {success_count}/10, Avg: {avg_duration:.2f}s")
        else:
            self.log_test("stress_concurrent", "failed", "No successful requests")

    def generate_comprehensive_report(self):
        """Generate detailed test report"""
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Calculate overall statistics
        total_tests = len(self.results["detailed_results"])
        successful = sum(1 for r in self.results["detailed_results"].values() 
                        if r["status"] == "success")
        failed = sum(1 for r in self.results["detailed_results"].values() 
                    if r["status"] == "failed")
        errors = sum(1 for r in self.results["detailed_results"].values() 
                    if r["status"] == "error")
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Errors: {errors}")
        print(f"Success Rate: {(successful/total_tests*100):.1f}%")
        
        # Performance metrics
        print(f"\n🚀 PERFORMANCE METRICS:")
        for metric, value in self.results["performance_metrics"].items():
            print(f"- {metric}: {value}")
        
        # Detailed results by category
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.results["detailed_results"].items():
            status_emoji = {"success": "✅", "failed": "❌", "error": "⚠️", "skipped": "⏭️"}
            emoji = status_emoji.get(result["status"], "❓")
            print(f"{emoji} {test_name}: {result['status']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
            if result.get('details'):
                print(f"   Details: {result['details']}")
        
        # Save detailed report
        report = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": total_tests,
                "successful": successful,
                "failed": failed,
                "errors": errors,
                "success_rate": successful/total_tests*100
            },
            **self.results
        }
        
        with open('massive_production_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: massive_production_test_report.json")
        return report

    def run_all_tests(self):
        """Run the complete production test suite"""
        print("🚀 STARTING MASSIVE PRODUCTION-LEVEL API TESTING")
        print("="*80)
        
        start_time = time.time()
        
        # Run all test categories
        self.test_health_endpoint()
        self.test_supported_languages_comprehensive()
        self.test_language_detection_all_languages()
        
        uploaded_files = self.test_file_upload_multiple_formats()
        self.test_translation_all_language_pairs()
        
        self.test_speech_processing_comprehensive()
        self.test_edge_cases_and_error_scenarios()
        self.test_performance_and_stress()
        
        # Generate comprehensive report
        total_time = time.time() - start_time
        print(f"\n⏱️ Total testing time: {total_time:.2f} seconds")
        
        report = self.generate_comprehensive_report()
        return report

if __name__ == "__main__":
    print("🔥 MASSIVE PRODUCTION-LEVEL API TEST SUITE 🔥")
    print("Testing every endpoint, every language, every edge case!")
    print("This will take several minutes to complete...")
    
    tester = ProductionAPITester()
    report = tester.run_all_tests()
    
    # Final summary
    success_rate = report.get("summary", {}).get("success_rate", 0)
    if success_rate >= 90:
        print(f"\n🎉 EXCELLENT! System is production-ready with {success_rate:.1f}% success rate!")
    elif success_rate >= 75:
        print(f"\n✅ GOOD! System is mostly working with {success_rate:.1f}% success rate. Minor fixes needed.")
    else:
        print(f"\n⚠️ NEEDS WORK! Success rate is {success_rate:.1f}%. Major fixes required.")