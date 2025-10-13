#!/usr/bin/env python3
"""
QUICK INDICTRANS2 TEST
Test the fixed IndicTrans2 implementation
"""

import sys
import os

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_indictrans2():
    """Test IndicTrans2 with proper preprocessing"""
    
    print("🔧 TESTING FIXED INDICTRANS2")
    print("="*40)
    
    try:
        from app.services.nlp_engine import get_nlp_engine
        engine = get_nlp_engine()
        
        # Test phrases
        test_texts = [
            "Hello, how are you?",
            "The weather is nice today",
            "Thank you very much",
            "Good morning",
            "I need help"
        ]
        
        # Test languages
        test_langs = ["hi", "bn", "ta", "te"]
        
        print(f"📥 Loading IndicTrans2 model...")
        success = engine.load_indic_trans2_model("en_to_indic")
        
        if not success:
            print("❌ Model loading failed")
            return False
            
        print("✅ Model loaded successfully")
        
        print(f"\n🔄 Testing translations...")
        
        for text in test_texts[:3]:  # Test first 3
            print(f"\n  📝 Text: '{text}'")
            
            for lang in test_langs[:2]:  # Test 2 languages
                print(f"    ├─ English → {lang}... ", end="")
                
                try:
                    result = engine.translate_with_indic_trans2(text, "en", lang)
                    
                    if result and "translated_text" in result:
                        translated = result["translated_text"]
                        model_used = result.get("model_used", "unknown")
                        is_emergency = result.get("is_emergency", False)
                        
                        if translated != text and not is_emergency:
                            print("✅ SUCCESS")
                            print(f"      └─ Result: {translated}")
                        elif is_emergency:
                            print("🔄 EMERGENCY")
                            print(f"      └─ Result: {translated}")
                        else:
                            print("⚠️ NO CHANGE")
                    else:
                        print("❌ FAILED")
                        
                except Exception as e:
                    print(f"❌ ERROR: {str(e)[:50]}...")
        
        print(f"\n✅ Test completed")
        return True
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    test_indictrans2()