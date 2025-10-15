#!/usr/bin/env python3
"""
Performance Optimization Test Script
Compares standard vs optimized video localization performance
"""

import requests
import json
import time
import os
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_performance_comparison():
    """Test performance comparison between standard and optimized endpoints"""
    print("🚀 Performance Optimization Test")
    print("=" * 60)
    print("Comparing standard vs optimized video localization")
    print("=" * 60)
    
    # Create a test video file (you can replace this with an actual video file)
    test_video_content = b"dummy video content for testing"
    test_filename = "test_video.mp4"
    
    try:
        # Create test file
        with open(test_filename, 'wb') as f:
            f.write(test_video_content)
        
        file_size = os.path.getsize(test_filename)
        print(f"📁 Created test file: {test_filename} ({file_size} bytes)")
        
        # Test 1: Standard video localization
        print("\n📝 Test 1: Standard Video Localization")
        print("-" * 40)
        
        start_time = time.time()
        
        with open(test_filename, 'rb') as f:
            files = {"file": f}
            data = {
                "target_language": "hi",
                "domain": "general",
                "include_subtitles": "true",
                "include_dubbed_audio": "false"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/video/localize",
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout
                )
                
                standard_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Standard endpoint successful")
                    print(f"📊 Processing time: {standard_time:.2f}s")
                    print(f"📊 Response time: {result.get('processing_time_seconds', 0):.2f}s")
                    print(f"📊 Status: {result.get('status')}")
                else:
                    print(f"❌ Standard endpoint failed: {response.status_code}")
                    print(f"📊 Time to failure: {standard_time:.2f}s")
                    standard_time = None
                    
            except requests.exceptions.Timeout:
                standard_time = time.time() - start_time
                print(f"⏰ Standard endpoint timed out after {standard_time:.2f}s")
            except Exception as e:
                standard_time = time.time() - start_time
                print(f"❌ Standard endpoint error: {e}")
                print(f"📊 Time to error: {standard_time:.2f}s")
        
        # Test 2: Optimized video localization (fast quality)
        print("\n📝 Test 2: Optimized Video Localization (Fast)")
        print("-" * 40)
        
        start_time = time.time()
        
        with open(test_filename, 'rb') as f:
            files = {"file": f}
            data = {
                "target_language": "hi",
                "domain": "general",
                "include_subtitles": "true",
                "include_dubbed_audio": "false",
                "quality_preference": "fast"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/video/localize-fast",
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout
                )
                
                optimized_fast_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Optimized (fast) endpoint successful")
                    print(f"📊 Processing time: {optimized_fast_time:.2f}s")
                    print(f"📊 Response time: {result.get('processing_time_seconds', 0):.2f}s")
                    print(f"📊 Model used: {result.get('model_used', 'unknown')}")
                    print(f"📊 Quality preference: {result.get('quality_preference', 'unknown')}")
                    print(f"📊 Performance improvements: {result.get('performance_improvements', {})}")
                else:
                    print(f"❌ Optimized (fast) endpoint failed: {response.status_code}")
                    print(f"📊 Time to failure: {optimized_fast_time:.2f}s")
                    optimized_fast_time = None
                    
            except requests.exceptions.Timeout:
                optimized_fast_time = time.time() - start_time
                print(f"⏰ Optimized (fast) endpoint timed out after {optimized_fast_time:.2f}s")
            except Exception as e:
                optimized_fast_time = time.time() - start_time
                print(f"❌ Optimized (fast) endpoint error: {e}")
                print(f"📊 Time to error: {optimized_fast_time:.2f}s")
        
        # Test 3: Optimized video localization (balanced quality)
        print("\n📝 Test 3: Optimized Video Localization (Balanced)")
        print("-" * 40)
        
        start_time = time.time()
        
        with open(test_filename, 'rb') as f:
            files = {"file": f}
            data = {
                "target_language": "hi",
                "domain": "general",
                "include_subtitles": "true",
                "include_dubbed_audio": "false",
                "quality_preference": "balanced"
            }
            
            try:
                response = requests.post(
                    f"{BASE_URL}/video/localize-fast",
                    files=files,
                    data=data,
                    timeout=300  # 5 minute timeout
                )
                
                optimized_balanced_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Optimized (balanced) endpoint successful")
                    print(f"📊 Processing time: {optimized_balanced_time:.2f}s")
                    print(f"📊 Response time: {result.get('processing_time_seconds', 0):.2f}s")
                    print(f"📊 Model used: {result.get('model_used', 'unknown')}")
                    print(f"📊 Quality preference: {result.get('quality_preference', 'unknown')}")
                else:
                    print(f"❌ Optimized (balanced) endpoint failed: {response.status_code}")
                    print(f"📊 Time to failure: {optimized_balanced_time:.2f}s")
                    optimized_balanced_time = None
                    
            except requests.exceptions.Timeout:
                optimized_balanced_time = time.time() - start_time
                print(f"⏰ Optimized (balanced) endpoint timed out after {optimized_balanced_time:.2f}s")
            except Exception as e:
                optimized_balanced_time = time.time() - start_time
                print(f"❌ Optimized (balanced) endpoint error: {e}")
                print(f"📊 Time to error: {optimized_balanced_time:.2f}s")
        
        # Performance comparison
        print("\n" + "=" * 60)
        print("📊 Performance Comparison Results")
        print("=" * 60)
        
        times = {
            "Standard": standard_time,
            "Optimized (Fast)": optimized_fast_time,
            "Optimized (Balanced)": optimized_balanced_time
        }
        
        successful_tests = {k: v for k, v in times.items() if v is not None}
        
        if successful_tests:
            fastest_time = min(successful_tests.values())
            fastest_method = min(successful_tests, key=successful_tests.get)
            
            print(f"🏆 Fastest method: {fastest_method} ({fastest_time:.2f}s)")
            
            for method, time_taken in times.items():
                if time_taken is not None:
                    improvement = ((time_taken - fastest_time) / time_taken) * 100 if time_taken > 0 else 0
                    print(f"📈 {method}: {time_taken:.2f}s ({improvement:+.1f}% vs fastest)")
                else:
                    print(f"❌ {method}: Failed or timed out")
            
            # Calculate improvements over standard
            if standard_time is not None and standard_time > 0:
                print(f"\n🚀 Performance Improvements over Standard:")
                for method, time_taken in successful_tests.items():
                    if method != "Standard" and time_taken is not None:
                        improvement = ((standard_time - time_taken) / standard_time) * 100
                        print(f"   {method}: {improvement:+.1f}% faster")
        else:
            print("❌ No successful tests to compare")
        
        print("\n💡 Recommendations:")
        print("   - Use /video/localize-fast with quality_preference='fast' for quick processing")
        print("   - Use /video/localize-fast with quality_preference='balanced' for good quality/speed balance")
        print("   - Use /video/localize-fast with quality_preference='quality' for best quality (slower)")
        print("   - Standard /video/localize uses large-v3 model (slowest but highest quality)")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
            print(f"🧹 Cleaned up test file: {test_filename}")

def test_server_performance():
    """Test server performance metrics"""
    print("\n🔍 Server Performance Metrics")
    print("=" * 60)
    
    try:
        # Get server stats
        response = requests.get(f"{BASE_URL}/logs/server-stats", timeout=30)
        if response.status_code == 200:
            stats = response.json()
            server_stats = stats.get('server_stats', {})
            
            print(f"📊 Server Uptime: {server_stats.get('uptime_human', 'unknown')}")
            print(f"📊 Total Requests: {server_stats.get('total_requests', 0)}")
            print(f"📊 Requests/sec: {server_stats.get('requests_per_second', 0):.2f}")
            print(f"📊 Data Transferred: {server_stats.get('total_data_transferred_mb', 0):.2f} MB")
            print(f"📊 Data Rate: {server_stats.get('data_transfer_rate_mbps', 0):.4f} Mbps")
            
            transfer_stats = stats.get('transfer_stats', {})
            print(f"📊 Active Transfers: {transfer_stats.get('active_transfers', 0)}")
        else:
            print(f"❌ Could not get server stats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting server stats: {e}")

if __name__ == "__main__":
    print("🧪 Performance Optimization Test Suite")
    print("This test compares standard vs optimized video localization performance")
    print()
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_performance_comparison()
    test_server_performance()
    
    print("\n🎉 Performance test completed!")
    print("Check the results above to see the performance improvements.")
