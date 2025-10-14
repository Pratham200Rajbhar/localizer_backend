#!/usr/bin/env python3
"""
Comprehensive Language Detection Test
Tests all 22 Indian languages + English
"""

import requests
import json
import time

# Comprehensive test data for all languages
TEST_DATA = {
    "en": [
        "Welcome to the AI-powered multilingual content localization engine.",
        "This system can translate documents across 22 Indian languages with high accuracy.",
        "Hello, how are you today? I hope you are doing well.",
        "The weather is nice today. Let's go for a walk in the park."
    ],
    "hi": [
        "नमस्ते, आप कैसे हैं? मैं ठीक हूँ।",
        "यह एक बहुभाषी सामग्री स्थानीयकरण इंजन है।",
        "आज मौसम बहुत अच्छा है। चलिए पार्क में टहलने चलते हैं।",
        "कृपया मुझे मदद करें। मुझे समझ नहीं आ रहा।"
    ],
    "bn": [
        "আমি ভালো আছি, ধন্যবাদ।",
        "এটি একটি বহুভাষিক কন্টেন্ট লোকালাইজেশন ইঞ্জিন।",
        "আজ আবহাওয়া খুব ভালো। চলুন পার্কে হাঁটতে যাই।",
        "দয়া করে আমাকে সাহায্য করুন। আমি বুঝতে পারছি না।"
    ],
    "ta": [
        "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? நான் நன்றாக இருக்கிறேன்।",
        "இது ஒரு பல்மொழி உள்ளடக்கம் உள்ளூர்மயமாக்கல் இயந்திரம்.",
        "இன்று வானிலை மிகவும் நன்றாக உள்ளது। பூங்காவில் நடக்கலாம்।",
        "தயவுசெய்து எனக்கு உதவுங்கள்। எனக்கு புரியவில்லை।"
    ],
    "te": [
        "హలో, మీరు ఎలా ఉన్నారు? నేను బాగున్నాను.",
        "ఇది ఒక బహుభాషా కంటెంట్ లోకలైజేషన్ ఇంజిన్.",
        "ఈ రోజు వాతావరణం చాలా బాగుంది। పార్కులో నడుద్దాం।",
        "దయచేసి నాకు సహాయం చేయండి। నాకు అర్థం కావడం లేదు।"
    ],
    "gu": [
        "હેલો, તમે કેમ છો? હું બરાબર છું.",
        "આ એક બહુભાષી કન્ટેન્ટ લોકલાઇઝેશન એન્જિન છે.",
        "આજે હવામાન ખૂબ સારું છે। ચાલો પાર્કમાં ચાલીએ।",
        "કૃપા કરીને મને મદદ કરો। મને સમજાતું નથી।"
    ],
    "mr": [
        "हॅलो, तुम्ही कसे आहात? मी ठीक आहे.",
        "हे एक बहुभाषी सामग्री स्थानीयकरण इंजिन आहे.",
        "आज हवामान खूप छान आहे। चला पार्कमध्ये चालूया।",
        "कृपया मला मदत करा। मला समजत नाही।"
    ],
    "pa": [
        "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ? ਮੈਂ ਠੀਕ ਹਾਂ।",
        "ਇਹ ਇੱਕ ਬਹੁਭਾਸ਼ੀ ਸਮਗਰੀ ਲੋਕਲਾਈਜੇਸ਼ਨ ਇੰਜਨ ਹੈ।",
        "ਅੱਜ ਮੌਸਮ ਬਹੁਤ ਵਧੀਆ ਹੈ। ਚਲੋ ਪਾਰਕ ਵਿੱਚ ਚੱਲੀਏ।",
        "ਕਿਰਪਾ ਕਰਕੇ ਮੇਰੀ ਮਦਦ ਕਰੋ। ਮੈਨੂੰ ਸਮਝ ਨਹੀਂ ਆ ਰਿਹਾ।"
    ],
    "kn": [
        "ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ? ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ.",
        "ಇದು ಒಂದು ಬಹುಭಾಷಾ ವಿಷಯ ಸ್ಥಳೀಕರಣ ಎಂಜಿನ್.",
        "ಇಂದು ಹವಾಮಾನ ತುಂಬಾ ಚೆನ್ನಾಗಿದೆ। ಪಾರ್ಕ್ನಲ್ಲಿ ನಡೆಯೋಣ।",
        "ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಿ। ನನಗೆ ಅರ್ಥವಾಗುತ್ತಿಲ್ಲ।"
    ],
    "ml": [
        "നമസ്കാരം, നിങ്ങൾ എങ്ങനെയുണ്ട്? ഞാൻ നന്നായിരിക്കുന്നു.",
        "ഇത് ഒരു ബഹുഭാഷാ ഉള്ളടക്ക ലോക്കലൈസേഷൻ എഞ്ചിൻ ആണ്.",
        "ഇന്ന് കാലാവസ്ഥ വളരെ നല്ലതാണ്। പാർക്കിൽ നടക്കാം।",
        "ദയവായി എന്നെ സഹായിക്കുക। എനിക്ക് മനസ്സിലാകുന്നില്ല।"
    ],
    "or": [
        "ନମସ୍କାର, ଆପଣ କିପରି ଅଛନ୍ତି? ମୁଁ ଭଲ ଅଛି।",
        "ଏହା ଏକ ବହୁଭାଷା ବିଷୟବସ୍ତୁ ସ୍ଥାନୀୟକରଣ ଇଞ୍ଜିନ୍।",
        "ଆଜି ପାଣିପାଗ ବହୁତ ଭଲ। ଚାଲନ୍ତୁ ପାର୍କରେ ଚାଲିବା।",
        "ଦୟାକରି ମୋତେ ସାହାଯ୍ୟ କରନ୍ତୁ। ମୋର ବୁଝିବାରେ ଅସୁବିଧା ହେଉଛି।"
    ],
    "as": [
        "নমস্কাৰ, আপুনি কেনেকৈ আছে? মই ভালেই আছোঁ।",
        "এইটো এটা বহুভাষিক বিষয়বস্তু স্থানীয়কৰণ ইঞ্জিন।",
        "আজি বতৰ বৰ ভাল। আহক পাৰ্কত খোজ কঢ়া কৰোঁ।",
        "অনুগ্ৰহ কৰি মোক সহায় কৰক। মোৰ বুজিবলৈ অসুবিধা হৈছে।"
    ],
    "ur": [
        "السلام علیکم، آپ کیسے ہیں؟ میں ٹھیک ہوں۔",
        "یہ ایک کثیر لسانی مواد مقامی کاری انجن ہے۔",
        "آج موسم بہت اچھا ہے۔ چلیں پارک میں چلیں۔",
        "براہ کرم میری مدد کریں۔ مجھے سمجھ نہیں آ رہا۔"
    ],
    "ne": [
        "नमस्ते, तपाईं कसरी हुनुहुन्छ? म ठीक छु।",
        "यो एक बहुभाषी सामग्री स्थानीयकरण इन्जिन हो।",
        "आज मौसम धेरै राम्रो छ। पार्कमा हिडौं।",
        "कृपया मलाई मद्दत गर्नुहोस्। मलाई बुझ्न मुस्किल भइरहेको छ।"
    ],
    "sa": [
        "नमस्ते, भवान् कथं वर्तते? अहं कुशलः अस्मि।",
        "एतत् बहुभाषिकं विषयस्थानीयकरणयन्त्रम् अस्ति।",
        "अद्य वातावरणं बहु सुन्दरम् अस्ति। उद्याने चलामः।",
        "कृपया मां साहाय्यं कुर्वन्तु। मम बोधे क्लेशः भवति।"
    ],
    "brx": [
        "नमस्कार, नों कसे आसो? आं बेसी आसो।",
        "एथे बहुभाषिक सामग्री स्थानीयकरण इंजिन आसो।",
        "आजि मौसम बेसी बांगो आसो। पार्काव हाबो।",
        "कृपया आंखौ साहाय्य करो। आंखौ बुझनायाव क्लेश जायो।"
    ],
    "doi": [
        "नमस्कार, तुसी कैसे हो? मैं ठीक हां।",
        "ये एक बहुभाषी सामग्री स्थानीयकरण इंजिन है।",
        "आज मौसम बहुत अच्छा है। चलो पार्क में चलें।",
        "कृपया मेरी मदद करो। मुझे समझ नहीं आ रहा।"
    ],
    "ks": [
        "اسلام علیکم، تہِ کیہہ حال چھو؟ میں ٹھیک چھوں۔",
        "یہ ایک کثیر لسانی مواد مقامی کاری انجن چھو۔",
        "آج موسم بہت اچھا چھو۔ چلو پارک وچ چلو۔",
        "براہ کرم میری مدد کرو۔ مجھے سمجھ نہیں آ رہا۔"
    ],
    "kok": [
        "नमस्कार, तुमी कशें आसात? हांव बरें आसां।",
        "हें एक बहुभाषी सामग्री स्थानीयकरण इंजिन आसा।",
        "आज मौसम बरें आसा। चलो पार्कांत वचूं।",
        "कृपया म्हाका मजत करात। म्हाका समजना येना।"
    ],
    "mai": [
        "नमस्कार, अहाँ कहाँ छी? हम ठीक छी।",
        "ई एक बहुभाषी सामग्री स्थानीयकरण इंजिन छी।",
        "आज मौसम बहुत अच्छा छी। चलो पार्क में चलूं।",
        "कृपया हमरा मदद करूं। हमरा समझ नहीं आ रहल छी।"
    ],
    "mni": [
        "নমস্কাৰ, নুংগাইদা কদাৱা? ঈ য়াম্না।",
        "ঈগা এগা বহুভাষিক বিষয়বস্তু স্থানীয়কৰণ ইঞ্জিন।",
        "নুংগাইদা খুনা বৰ ভাল। পাৰ্কত খোজ কঢ়া কৰোঁ।",
        "অনুগ্ৰহ কৰি ঈগা সহায় কৰোঁ। ঈগা বুজিবলৈ অসুবিধা হৈছে।"
    ],
    "sat": [
        "नमस्कार, नों कसे आसो? आं बेसी आसो।",
        "एथे बहुभाषिक सामग्री स्थानीयकरण इंजिन आसो।",
        "आजि मौसम बेसी बांगो आसो। पार्काव हाबो।",
        "कृपया आंखौ साहाय्य करो। आंखौ बुझनायाव क्लेश जायो।"
    ],
    "sd": [
        "سلام علیکم، توهان ڪيئن آهيو؟ مان ٺيڪ آهيان۔",
        "هي هڪ ڪثير لساني مواد مقامي ڪاري انجن آهي۔",
        "اڄ موسم تمام چڱو آهي۔ اچو پارڪ ۾ هلون۔",
        "مهرباني ڪري مون کي مدد ڏيو۔ مون کي سمجهڻ ۾ مشڪل پئي رهي آهي۔"
    ]
}

def test_language_detection():
    """Test language detection for all languages"""
    print("🧪 Comprehensive Language Detection Test")
    print("=" * 60)
    
    total_tests = 0
    total_correct = 0
    results = {}
    
    for lang_code, test_texts in TEST_DATA.items():
        print(f"\n🔍 Testing {lang_code.upper()} ({len(test_texts)} samples)...")
        
        correct_count = 0
        lang_results = []
        
        for text in test_texts:
            try:
                response = requests.post(
                    "http://localhost:8000/detect-language",
                    headers={"Content-Type": "application/json"},
                    json={"text": text},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    detected = result.get("detected_language", "unknown")
                    confidence = result.get("confidence", 0.0)
                    correct = detected == lang_code
                    
                    if correct:
                        correct_count += 1
                    
                    lang_results.append({
                        "text": text[:30] + "..." if len(text) > 30 else text,
                        "expected": lang_code,
                        "detected": detected,
                        "confidence": confidence,
                        "correct": correct
                    })
                else:
                    lang_results.append({
                        "text": text[:30] + "..." if len(text) > 30 else text,
                        "expected": lang_code,
                        "detected": "ERROR",
                        "confidence": 0.0,
                        "correct": False,
                        "error": f"HTTP {response.status_code}"
                    })
                
                time.sleep(0.1)  # Small delay
                
            except Exception as e:
                lang_results.append({
                    "text": text[:30] + "..." if len(text) > 30 else text,
                    "expected": lang_code,
                    "detected": "ERROR",
                    "confidence": 0.0,
                    "correct": False,
                    "error": str(e)
                })
        
        accuracy = (correct_count / len(test_texts)) * 100 if test_texts else 0
        results[lang_code] = {
            "total": len(test_texts),
            "correct": correct_count,
            "accuracy": accuracy,
            "results": lang_results
        }
        
        total_tests += len(test_texts)
        total_correct += correct_count
        
        # Print summary
        status = "✅" if accuracy >= 90 else "⚠️" if accuracy >= 70 else "❌"
        print(f"   {status} Accuracy: {accuracy:.1f}% ({correct_count}/{len(test_texts)})")
        
        # Show failed detections
        failed = [r for r in lang_results if not r["correct"]]
        if failed:
            print(f"   ❌ Failed detections:")
            for fail in failed[:2]:  # Show first 2 failures
                print(f"      Expected: {fail['expected']}, Got: {fail['detected']} (conf: {fail['confidence']:.2f})")
    
    # Overall summary
    overall_accuracy = (total_correct / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 OVERALL RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Correct Detections: {total_correct}")
    print(f"Overall Accuracy: {overall_accuracy:.1f}%")
    
    # Language-wise summary
    print(f"\n📋 LANGUAGE-WISE ACCURACY:")
    for lang_code, result in results.items():
        status = "✅" if result["accuracy"] >= 90 else "⚠️" if result["accuracy"] >= 70 else "❌"
        print(f"   {status} {lang_code.upper()}: {result['accuracy']:.1f}%")
    
    # Identify problematic languages
    problematic = [(lang, result) for lang, result in results.items() if result["accuracy"] < 90]
    if problematic:
        print(f"\n⚠️  LANGUAGES NEEDING IMPROVEMENT (Accuracy < 90%):")
        for lang, result in problematic:
            print(f"   - {lang.upper()}: {result['accuracy']:.1f}%")
    
    # Save detailed results
    with open("comprehensive_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: comprehensive_test_results.json")
    
    return results

if __name__ == "__main__":
    try:
        results = test_language_detection()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
