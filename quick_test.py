#!/usr/bin/env python3
"""
Quick server test to check if basic endpoints work
"""

import asyncio
import httpx
import time

async def quick_test():
    """Quick test of basic endpoints"""
    base_url = "http://localhost:8000"  # Use default port
    
    print("🧪 Quick Backend Test")
    print("=" * 30)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            print("Testing /health endpoint...")
            try:
                response = await client.get(f"{base_url}/health")
                if response.status_code == 200:
                    print("✅ Health endpoint working")
                else:
                    print(f"❌ Health endpoint failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Health endpoint error: {e}")
            
            # Test supported languages
            print("Testing /supported-languages endpoint...")
            try:
                response = await client.get(f"{base_url}/supported-languages")
                if response.status_code == 200:
                    languages = response.json()
                    print(f"✅ Got {len(languages)} supported languages")
                else:
                    print(f"❌ Languages endpoint failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Languages endpoint error: {e}")
            
            # Test OpenAPI docs
            print("Testing /docs endpoint...")
            try:
                response = await client.get(f"{base_url}/docs")
                if response.status_code == 200:
                    print("✅ API docs accessible")
                else:
                    print(f"❌ API docs failed: {response.status_code}")
            except Exception as e:
                print(f"❌ API docs error: {e}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())