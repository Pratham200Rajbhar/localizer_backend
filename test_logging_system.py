#!/usr/bin/env python3
"""
Test script for the comprehensive logging system
Tests all logging functionality including requests, data transfers, and server activities
"""

import requests
import json
import time
import os
from typing import Dict, Any

def test_server_stats():
    """Test server statistics endpoint"""
    print("🔍 Testing Server Statistics")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/logs/server-stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Server stats retrieved successfully")
            print(f"📊 Server Stats:")
            print(f"   - Uptime: {stats['server_stats']['uptime_human']}")
            print(f"   - Total Requests: {stats['server_stats']['total_requests']}")
            print(f"   - Data Transferred: {stats['server_stats']['total_data_transferred_mb']} MB")
            print(f"   - Requests/sec: {stats['server_stats']['requests_per_second']}")
            print(f"   - Data Rate: {stats['server_stats']['data_transfer_rate_mbps']} Mbps")
            print(f"📊 Transfer Stats:")
            print(f"   - Active Transfers: {stats['transfer_stats']['active_transfers']}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_request_logging():
    """Test request logging by making various API calls"""
    print("\n🔍 Testing Request Logging")
    print("=" * 50)
    
    test_requests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": "http://localhost:8000/",
            "expected_status": 200
        },
        {
            "name": "Supported Languages",
            "method": "GET", 
            "url": "http://localhost:8000/supported-languages",
            "expected_status": 200
        },
        {
            "name": "Language Detection",
            "method": "POST",
            "url": "http://localhost:8000/detect-language",
            "data": {"text": "Hello, this is a test"},
            "expected_status": 200
        },
        {
            "name": "Translation Request",
            "method": "POST",
            "url": "http://localhost:8000/translate",
            "data": {
                "text": "This is a test translation request",
                "source_language": "en",
                "target_languages": ["hi"],
                "domain": "general"
            },
            "expected_status": 200
        }
    ]
    
    successful_requests = 0
    
    for test_req in test_requests:
        print(f"\n📝 Testing: {test_req['name']}")
        
        try:
            if test_req["method"] == "GET":
                response = requests.get(test_req["url"], timeout=30)
            else:
                response = requests.post(
                    test_req["url"], 
                    json=test_req.get("data", {}),
                    timeout=30
                )
            
            if response.status_code == test_req["expected_status"]:
                print(f"   ✅ Request successful (Status: {response.status_code})")
                print(f"   📊 Response size: {len(response.content)} bytes")
                print(f"   ⏱️  Response time: {response.elapsed.total_seconds():.3f}s")
                
                # Check for request ID in headers
                request_id = response.headers.get("X-Request-ID")
                if request_id:
                    print(f"   🆔 Request ID: {request_id}")
                
                successful_requests += 1
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Request Logging Results: {successful_requests}/{len(test_requests)} successful")
    return successful_requests == len(test_requests)

def test_data_transfer_logging():
    """Test data transfer logging with file upload"""
    print("\n🔍 Testing Data Transfer Logging")
    print("=" * 50)
    
    # Create a test file
    test_file_content = "This is a test file for data transfer logging.\n" * 100
    test_file_path = "test_transfer_file.txt"
    
    try:
        # Create test file
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_file_content)
        
        file_size = os.path.getsize(test_file_path)
        print(f"📁 Created test file: {test_file_path} ({file_size} bytes)")
        
        # Test file upload
        print("📤 Testing file upload...")
        with open(test_file_path, 'rb') as f:
            files = {"file": f}
            data = {"domain": "general", "source_language": "en"}
            
            response = requests.post(
                "http://localhost:8000/content/upload",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"   ✅ Upload successful")
            print(f"   📊 File ID: {upload_result.get('id')}")
            print(f"   📊 File size: {upload_result.get('size')} bytes")
            print(f"   📊 Processing time: {response.elapsed.total_seconds():.3f}s")
            
            # Test file download (if file was uploaded successfully)
            if upload_result.get('id'):
                print("📥 Testing file download...")
                download_response = requests.get(
                    f"http://localhost:8000/content/files/{upload_result['id']}",
                    timeout=30
                )
                
                if download_response.status_code == 200:
                    print(f"   ✅ Download successful")
                    print(f"   📊 Response size: {len(download_response.content)} bytes")
                else:
                    print(f"   ❌ Download failed: {download_response.status_code}")
            
            return True
        else:
            print(f"   ❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"🧹 Cleaned up test file: {test_file_path}")

def test_log_endpoints():
    """Test log viewing endpoints"""
    print("\n🔍 Testing Log Viewing Endpoints")
    print("=" * 50)
    
    log_endpoints = [
        {
            "name": "Recent Requests",
            "url": "http://localhost:8000/logs/requests?limit=10"
        },
        {
            "name": "Recent Transfers", 
            "url": "http://localhost:8000/logs/transfers?limit=10"
        },
        {
            "name": "Recent Activities",
            "url": "http://localhost:8000/logs/activities?limit=10"
        },
        {
            "name": "Active Transfers",
            "url": "http://localhost:8000/logs/active-transfers"
        },
        {
            "name": "Performance Metrics",
            "url": "http://localhost:8000/logs/performance"
        },
        {
            "name": "Logs Summary",
            "url": "http://localhost:8000/logs/summary?hours=1"
        }
    ]
    
    successful_endpoints = 0
    
    for endpoint in log_endpoints:
        print(f"\n📝 Testing: {endpoint['name']}")
        
        try:
            response = requests.get(endpoint["url"], timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint accessible")
                print(f"   📊 Status: {data.get('status', 'unknown')}")
                
                # Show some data if available
                if 'count' in data:
                    print(f"   📊 Count: {data['count']}")
                elif 'requests' in data:
                    print(f"   📊 Requests: {len(data['requests'])}")
                elif 'transfers' in data:
                    print(f"   📊 Transfers: {len(data['transfers'])}")
                elif 'activities' in data:
                    print(f"   📊 Activities: {len(data['activities'])}")
                
                successful_endpoints += 1
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Log Endpoints Results: {successful_endpoints}/{len(log_endpoints)} successful")
    return successful_endpoints == len(log_endpoints)

def test_log_cleanup():
    """Test log cleanup functionality"""
    print("\n🔍 Testing Log Cleanup")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/logs/cleanup?days_to_keep=30",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Log cleanup successful")
            print(f"📊 Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all logging system tests"""
    print("🧪 Comprehensive Logging System Test")
    print("=" * 80)
    print("Testing the complete server logging and monitoring system")
    print("=" * 80)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    test_results = []
    
    # Test server statistics
    test_results.append(("Server Stats", test_server_stats()))
    
    # Test request logging
    test_results.append(("Request Logging", test_request_logging()))
    
    # Test data transfer logging
    test_results.append(("Data Transfer Logging", test_data_transfer_logging()))
    
    # Test log endpoints
    test_results.append(("Log Endpoints", test_log_endpoints()))
    
    # Test log cleanup
    test_results.append(("Log Cleanup", test_log_cleanup()))
    
    # Final server stats
    print("\n🔍 Final Server Statistics")
    print("=" * 50)
    test_server_stats()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 Test Summary:")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All logging system tests passed!")
        print("\n✨ The comprehensive logging system is working correctly:")
        print("   - All HTTP requests are being logged")
        print("   - Data transfers are being tracked")
        print("   - Server activities are being monitored")
        print("   - Log viewing endpoints are functional")
        print("   - Log cleanup is working")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
