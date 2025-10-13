"""
Debug translation by checking the uploaded file
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_translation_debug():
    print("=== TRANSLATION DEBUG TEST ===")
    
    # Step 1: Upload a file
    print("\n1. Uploading test file...")
    test_content = "This is a simple test file for translation. Hello world! How are you today?"
    
    with open('debug_test.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    with open('debug_test.txt', 'rb') as f:
        files = {'file': ('debug_test.txt', f, 'text/plain')}
        data = {'domain': 'general'}
        response = requests.post(f"{BASE_URL}/content/upload", files=files, data=data)
    
    print(f"Upload Status: {response.status_code}")
    print(f"Upload Response: {response.text}")
    
    if response.status_code not in [200, 201]:
        print("Upload failed, stopping test")
        return
    
    file_info = response.json()
    file_id = file_info.get('id')
    print(f"File ID: {file_id}")
    print(f"File path: {file_info.get('path')}")
    
    # Step 2: Check if file exists at the path
    import os
    file_path = file_info.get('path')
    print(f"\n2. Checking file at path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"File content length: {len(content)}")
        print(f"File content: '{content[:100]}...'")
    
    # Step 3: Test direct translation with text (should work)
    print("\n3. Testing direct text translation...")
    data = {
        "text": "Hello, this is a test translation.",
        "source_language": "en",
        "target_languages": ["hi"],
        "domain": "general"
    }
    response = requests.post(f"{BASE_URL}/translate", json=data)
    print(f"Direct text Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Direct text translation works")
    else:
        print(f"❌ Direct text failed: {response.text}")
    
    # Step 4: Test file-based translation
    print("\n4. Testing file-based translation...")
    data = {
        "file_id": file_id,
        "source_language": "en", 
        "target_languages": ["hi"],
        "domain": "general"
    }
    response = requests.post(f"{BASE_URL}/translate", json=data)
    print(f"File-based Status: {response.status_code}")
    print(f"File-based Response: {response.text}")
    
    # Cleanup
    import os
    try:
        os.remove('debug_test.txt')
    except:
        pass

if __name__ == "__main__":
    test_translation_debug()