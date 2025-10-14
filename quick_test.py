#!/usr/bin/env python3
"""
Quick Language Detection Test
"""

import requests
import json

# Test a few key languages
test_cases = [
    ("en", "Welcome to the AI-powered multilingual content localization engine."),
    ("hi", "नमस्ते, आप कैसे हैं? मैं ठीक हूँ।"),
    ("bn", "আমি ভালো আছি, ধন্যবাদ।"),
    ("ta", "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?"),
    ("te", "హలో, మీరు ఎలా ఉన్నారు?"),
    ("gu", "હેલો, તમે કેમ છો?"),
    ("mr", "हॅलो, तुम्ही कसे आहात?"),
    ("pa", "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?"),
    ("kn", "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ?"),
    ("ml", "നമസ്കാരം, നിങ്ങൾ എങ്ങനെയുണ്ട്?"),
    ("or", "ନମସ୍କାର, ଆପଣ କିପରି ଅଛନ୍ତି?"),
    ("as", "নমস্কাৰ, আপুনি কেনেকৈ আছে?"),
    ("ur", "السلام علیکم، آپ کیسے ہیں؟"),
    ("ne", "नमस्ते, तपाईं कसरी हुनुहुन्छ?"),
    ("sa", "नमस्ते, भवान् कथं वर्तते?"),
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

print("🧪 Quick Language Detection Test")
print("=" * 50)

correct_count = 0
total_count = len(test_cases)

for lang_code, text in test_cases:
    if test_language(lang_code, text):
        correct_count += 1

accuracy = (correct_count / total_count) * 100
print(f"\n📊 Results: {correct_count}/{total_count} correct ({accuracy:.1f}%)")
