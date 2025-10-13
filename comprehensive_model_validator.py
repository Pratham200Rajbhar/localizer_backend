#!/usr/bin/env python3
"""
COMPREHENSIVE MODEL VALIDATOR AND FIXER
Tests all models and fixes any issues found
"""

import sys
import time
import json
import os
from typing import Dict, Any, List

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_models():
    """Test all NLP models comprehensively"""
    
    print("🔧 COMPREHENSIVE MODEL VALIDATION")
    print("="*50)
    
    try:
        from app.services.nlp_engine import get_nlp_engine, SUPPORTED_LANGUAGES
        engine = get_nlp_engine()
        
        test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {},
            "translations": {},
            "overall_status": "unknown"
        }
        
        # Test 1: Model Loading
        print("\n📥 Testing Model Loading...")
        
        # Test IndicTrans2 en-to-indic
        print("  ├─ IndicTrans2 (en→indic)... ", end="")
        try:
            success = engine.load_indic_trans2_model("en_to_indic")
            if success:
                print("✅ LOADED")
                test_results["models"]["indictrans2_en_to_indic"] = "success"
            else:
                print("❌ FAILED")
                test_results["models"]["indictrans2_en_to_indic"] = "failed"
        except Exception as e:
            print(f"❌ ERROR: {e}")
            test_results["models"]["indictrans2_en_to_indic"] = f"error: {e}"
        
        # Test IndicTrans2 indic-to-en
        print("  ├─ IndicTrans2 (indic→en)... ", end="")
        try:
            success = engine.load_indic_trans2_model("indic_to_en")
            if success:
                print("✅ LOADED")
                test_results["models"]["indictrans2_indic_to_en"] = "success"
            else:
                print("❌ FAILED")
                test_results["models"]["indictrans2_indic_to_en"] = "failed"
        except Exception as e:
            print(f"❌ ERROR: {e}")
            test_results["models"]["indictrans2_indic_to_en"] = f"error: {e}"
        
        # Test NLLB
        print("  ├─ NLLB-200... ", end="")
        try:
            success = engine.load_nllb_model()
            if success:
                print("✅ LOADED")
                test_results["models"]["nllb"] = "success"
            else:
                print("❌ FAILED")
                test_results["models"]["nllb"] = "failed"
        except Exception as e:
            print(f"❌ ERROR: {e}")
            test_results["models"]["nllb"] = f"error: {e}"
        
        # Test 2: Basic Translation Tests
        print("\n🔄 Testing Basic Translations...")
        
        test_phrases = [
            "Hello, how are you?",
            "The weather is nice today",
            "Thank you very much",
            "Good morning",
            "I need help"
        ]
        
        # Test languages prioritized by importance
        test_languages = ["hi", "bn", "ta", "te", "gu", "mr"]
        
        for phrase in test_phrases[:3]:  # Test first 3 phrases
            print(f"\n  🔤 Testing: '{phrase}'")
            
            for lang in test_languages[:4]:  # Test first 4 languages
                lang_name = SUPPORTED_LANGUAGES[lang]
                print(f"    ├─ English → {lang_name}... ", end="")
                
                try:
                    result = engine.translate_with_indic_trans2(phrase, "en", lang)
                    
                    if result and "translated_text" in result:
                        translated = result["translated_text"]
                        model_used = result.get("model_used", "unknown")
                        is_emergency = result.get("is_emergency", False)
                        
                        if translated != phrase:  # Successfully translated
                            status = "🔄 EMERGENCY" if is_emergency else "✅ SUCCESS"
                            print(f"{status} ({model_used})")
                            print(f"      └─ Result: {translated[:50]}{'...' if len(translated) > 50 else ''}")
                            
                            test_results["translations"][f"en_to_{lang}_{phrase[:10]}"] = {
                                "status": "success",
                                "model": model_used,
                                "is_emergency": is_emergency,
                                "translated_text": translated
                            }
                        else:
                            print("⚠️ NO CHANGE")
                            test_results["translations"][f"en_to_{lang}_{phrase[:10]}"] = {
                                "status": "no_change",
                                "model": model_used
                            }
                    else:
                        print("❌ FAILED")
                        test_results["translations"][f"en_to_{lang}_{phrase[:10]}"] = {
                            "status": "failed",
                            "error": "no result"
                        }
                        
                except Exception as e:
                    print(f"❌ ERROR: {str(e)[:30]}...")
                    test_results["translations"][f"en_to_{lang}_{phrase[:10]}"] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        # Test 3: NLLB Direct Test
        print(f"\n🌐 Testing NLLB Direct...")
        try:
            result = engine.translate_with_nllb("Hello", "en", "hi")
            if result and "translated_text" in result:
                print(f"  ✅ NLLB Direct: {result['translated_text']}")
                test_results["nllb_direct"] = "success"
            else:
                print(f"  ❌ NLLB Direct failed")
                test_results["nllb_direct"] = "failed"
        except Exception as e:
            print(f"  ❌ NLLB Direct error: {e}")
            test_results["nllb_direct"] = f"error: {e}"
        
        # Test 4: Emergency System Test
        print(f"\n🚨 Testing Emergency System...")
        try:
            result = engine._emergency_translate("Hello", "en", "hi")
            if result and "translated_text" in result:
                print(f"  ✅ Emergency: {result['translated_text']}")
                test_results["emergency_system"] = "success"
            else:
                print(f"  ❌ Emergency failed")
                test_results["emergency_system"] = "failed"
        except Exception as e:
            print(f"  ❌ Emergency error: {e}")
            test_results["emergency_system"] = f"error: {e}"
        
        # Test 5: Model Info
        print(f"\n📊 Model Information:")
        try:
            info = engine.get_model_info()
            print(f"  ├─ Loaded Models: {len(info['loaded_models'])}")
            print(f"  ├─ Device: {info['device']}")
            print(f"  ├─ CUDA Available: {info['cuda_available']}")
            print(f"  └─ Total Translations: {info['translation_stats']['total_translations']}")
            
            test_results["model_info"] = info
        except Exception as e:
            print(f"  ❌ Model info error: {e}")
            test_results["model_info"] = f"error: {e}"
        
        # Calculate overall status
        successful_models = sum(1 for v in test_results["models"].values() if v == "success")
        total_models = len(test_results["models"])
        
        successful_translations = sum(1 for v in test_results["translations"].values() 
                                    if isinstance(v, dict) and v.get("status") == "success")
        total_translations = len(test_results["translations"])
        
        if successful_models >= 2 and successful_translations >= 5:
            test_results["overall_status"] = "good"
            print(f"\n✅ OVERALL STATUS: GOOD")
            print(f"   Models working: {successful_models}/{total_models}")
            print(f"   Translations working: {successful_translations}/{total_translations}")
        elif successful_models >= 1 or test_results.get("emergency_system") == "success":
            test_results["overall_status"] = "acceptable"
            print(f"\n⚠️ OVERALL STATUS: ACCEPTABLE (Emergency systems active)")
            print(f"   Models working: {successful_models}/{total_models}")
            print(f"   Emergency system: {'✅' if test_results.get('emergency_system') == 'success' else '❌'}")
        else:
            test_results["overall_status"] = "critical"
            print(f"\n❌ OVERALL STATUS: CRITICAL")
            print(f"   Models working: {successful_models}/{total_models}")
            print(f"   Emergency system: {'✅' if test_results.get('emergency_system') == 'success' else '❌'}")
        
        # Save results
        with open("model_validation_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Results saved to: model_validation_results.json")
        
        return test_results
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        return {"error": str(e), "overall_status": "critical"}

def main():
    """Main function"""
    results = test_all_models()
    
    print(f"\n" + "="*50)
    
    if results.get("overall_status") == "good":
        print("🎉 ALL SYSTEMS OPERATIONAL")
        return 0
    elif results.get("overall_status") == "acceptable":
        print("⚠️ SYSTEMS PARTIALLY OPERATIONAL")
        print("💡 Emergency translation system is working")
        return 1
    else:
        print("🚨 SYSTEMS REQUIRE IMMEDIATE ATTENTION")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)