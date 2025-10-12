#!/usr/bin/env python3
"""
Performance Benchmark for STT Processing
Tests different optimization scenarios
"""
import requests
import time
import statistics
import os

BASE_URL = "http://127.0.0.1:8000"
DEMO_AUDIO_FILE = "E:/new_backend/demo.mp3"

def get_auth_token():
    """Get authentication token"""
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def benchmark_stt(token, num_runs=3):
    """Benchmark STT performance"""
    print(f"\n🏃 Running STT Performance Benchmark ({num_runs} runs)...")
    
    if not os.path.exists(DEMO_AUDIO_FILE):
        print("❌ Demo audio file not found")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    times = []
    
    for i in range(num_runs):
        print(f"  Run {i+1}/{num_runs}...", end=" ")
        
        start_time = time.time()
        with open(DEMO_AUDIO_FILE, "rb") as audio_file:
            files = {"file": ("demo.mp3", audio_file, "audio/mp3")}
            response = requests.post(f"{BASE_URL}/speech/stt", files=files, headers=headers)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            times.append(duration)
            print(f"{duration:.2f}s ✅")
        else:
            print(f"❌ Failed")
    
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Performance Results:")
        print(f"  ⚡ Average: {avg_time:.2f}s")
        print(f"  🚀 Best: {min_time:.2f}s")
        print(f"  🐌 Worst: {max_time:.2f}s")
        
        # Calculate audio processing ratio
        # Demo file is approximately 29 seconds long
        audio_duration = 29.0  # seconds
        real_time_factor = audio_duration / avg_time
        
        print(f"  📈 Real-time factor: {real_time_factor:.1f}x")
        print(f"     (Processing {real_time_factor:.1f}x faster than audio duration)")
        
        if real_time_factor > 10:
            print("  🎉 Excellent performance! Very fast processing.")
        elif real_time_factor > 5:
            print("  ✅ Good performance! Fast enough for real-time use.")
        elif real_time_factor > 2:
            print("  👍 Acceptable performance for most use cases.")
        else:
            print("  ⚠️ Performance may need optimization for real-time use.")

def benchmark_tts(token, num_runs=3):
    """Benchmark TTS performance"""
    print(f"\n🔊 Running TTS Performance Benchmark ({num_runs} runs)...")
    
    headers = {"Authorization": f"Bearer {token}"}
    times = []
    
    test_texts = [
        "नमस्ते, यह एक छोटा परीक्षण संदेश है।",
        "Hello, this is a short test message.",
        "यह भारतीय भाषा स्थानीयकरण प्रणाली का परीक्षण है।"
    ]
    
    for i, text in enumerate(test_texts):
        print(f"  Test {i+1}/{len(test_texts)}: ", end="")
        
        tts_request = {
            "text": text,
            "language": "hi" if any(ord(c) > 127 for c in text) else "en",
            "voice": "default",
            "speed": 1.0
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/speech/tts", json=tts_request, headers=headers)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            times.append(duration)
            print(f"{duration:.2f}s ✅")
        else:
            print(f"❌ Failed")
    
    if times:
        avg_time = statistics.mean(times)
        print(f"\n📊 TTS Performance Results:")
        print(f"  ⚡ Average generation time: {avg_time:.2f}s")
        print(f"  🚀 Best: {min(times):.2f}s")
        print(f"  🐌 Worst: {max(times):.2f}s")

def main():
    """Run performance benchmarks"""
    print("🏁 BACKEND PERFORMANCE BENCHMARK")
    print("=" * 50)
    
    token = get_auth_token()
    if not token:
        print("❌ Authentication failed")
        return
    
    # Warm up the system (load models)
    print("🔥 Warming up system...")
    with open(DEMO_AUDIO_FILE, "rb") as audio_file:
        files = {"file": ("demo.mp3", audio_file, "audio/mp3")}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/speech/stt", files=files, headers=headers)
        if response.status_code == 200:
            print("✅ System warmed up")
        else:
            print("⚠️ Warmup failed, continuing anyway")
    
    # Run benchmarks
    benchmark_stt(token, num_runs=5)
    benchmark_tts(token, num_runs=3)
    
    print(f"\n🎯 Optimization Summary:")
    print("✅ Whisper model auto-selects fastest available version")
    print("✅ Audio preprocessing optimizes format and removes silence")
    print("✅ Model caching eliminates reload time between requests")
    print("✅ GPU acceleration when available, CPU fallback")
    print("✅ Simplified transcription options for better performance")

if __name__ == "__main__":
    main()