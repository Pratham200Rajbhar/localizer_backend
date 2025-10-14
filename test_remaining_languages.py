#!/usr/bin/env python3
"""
Test remaining Indian languages
"""

import requests
import json

# Test remaining languages
test_cases = [
    ("brx", "नमस्कार, नों कसे आसो? आं बेसी आसो।"),
    ("doi", "नमस्कार, तुसी कैसे हो? मैं ठीक हां।"),
    ("ks", "اسلام علیکم، تہِ کیہہ حال چھو؟ میں ٹھیک چھوں۔"),
    ("kok", "नमस्कार, तुमी कशें आसात? हांव बरें आसां।"),
    ("mai", "नमस्कार, अहाँ कहाँ छी? हम ठीक छी।"),
    ("mni", "নমস্কাৰ, নুংগাইদা কদাৱা? ঈ য়াম্না।"),
    ("sat", "नमस्कार, नों कसे आसो? आं बेसी आसो।"),
    ("sd", "سلام علیکم، توهان ڪيئن آهيو؟ مان ٺيڪ آهيان۔"),
]

def test_language(lang_code, text):
    try:
        response = requests.post(
            "http://localhost:8000/detect-language",
            headers={"Content-Type": "application/json"},
            json={"text": text},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            detected = result.get("detected_language", "unknown")
            confidence = result.get("confidence", 0.0)
            correct = detected == lang_code
            status = "✅" if correct else "❌"
            print(f"{status} {lang_code.upper()}: Expected {lang_code}, Got {detected} (conf: {confidence:.2f})")
            return correct
        else:
            print(f"❌ {lang_code.upper()}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {lang_code.upper()}: Error - {e}")
        return False

print("🧪 Testing Remaining Indian Languages")
print("=" * 50)

correct_count = 0
total_count = len(test_cases)

for lang_code, text in test_cases:
    if test_language(lang_code, text):
        correct_count += 1

accuracy = (correct_count / total_count) * 100
print(f"\n📊 Results: {correct_count}/{total_count} correct ({accuracy:.1f}%)")
