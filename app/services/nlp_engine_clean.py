"""
Simplified NLP Translation Engine for 22 Indian Languages
Clean and efficient translation using IndicTrans2 models
"""
import os
from typing import Dict, List

from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger

# Language detection
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    app_logger.warning("Language detection not available - using fallback")

# PyTorch for AI models
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    TORCH_AVAILABLE = True
    app_logger.info(f"PyTorch available - Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
except ImportError:
    TORCH_AVAILABLE = False
    app_logger.warning("PyTorch/Transformers not available")

settings = get_settings()


class SimpleNLPEngine:
    """
    Simplified NLP engine for Indian language translation
    """
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        app_logger.info(f"NLP Engine initialized on {self.device}")

    def detect_language(self, text: str) -> Dict:
        """Simple language detection"""
        if not text or len(text.strip()) < 3:
            return {
                "detected_language": "unknown",
                "language_name": "Unknown", 
                "confidence": 0.0
            }

        # Clean text for detection
        clean_text = text.strip()[:500]  # Limit for speed
        
        if LANGDETECT_AVAILABLE:
            try:
                detected = detect(clean_text)
                
                if detected in SUPPORTED_LANGUAGES:
                    return {
                        "detected_language": detected,
                        "language_name": SUPPORTED_LANGUAGES[detected],
                        "confidence": 0.9
                    }
                elif detected == "en":
                    return {
                        "detected_language": "en", 
                        "language_name": "English",
                        "confidence": 0.9
                    }
            except Exception as e:
                app_logger.warning(f"Language detection failed: {e}")
        
        # Fallback to Hindi for Indic scripts
        return {
            "detected_language": "hi",
            "language_name": "Hindi",
            "confidence": 0.5
        }

    def load_model(self, direction: str) -> bool:
        """Load translation model for direction (en-indic or indic-en)"""
        if not TORCH_AVAILABLE:
            app_logger.error("PyTorch not available - cannot load models")
            return False
            
        if direction in self.models:
            return True
            
        try:
            model_name = f"IndicTrans2-{direction}-1B"
            model_path = self._get_model_path(model_name)
            
            app_logger.info(f"Loading {model_name}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
            
            # Load model
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cuda":
                model = model.cuda()
            
            model.eval()
            
            self.models[direction] = model
            self.tokenizers[direction] = tokenizer
            
            app_logger.info(f"Model {model_name} loaded successfully")
            return True
            
        except Exception as e:
            app_logger.error(f"Failed to load model {direction}: {e}")
            return False

    def _get_model_path(self, model_name: str) -> str:
        """Get model path with fallback to HuggingFace"""
        local_paths = [
            f"saved_model/{model_name}",
            f"models/{model_name}"
        ]
        
        for path in local_paths:
            if os.path.exists(path):
                return path
        
        # Fallback to HuggingFace
        model_map = {
            "IndicTrans2-en-indic-1B": "ai4bharat/IndicTrans2-en-indic-1B",
            "IndicTrans2-indic-en-1B": "ai4bharat/IndicTrans2-indic-en-1B"
        }
        return model_map.get(model_name, f"ai4bharat/{model_name}")

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Translate text between languages"""
        if not text or not text.strip():
            return {
                "translated_text": "",
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.0,
                "model_used": "none"
            }

        # Determine translation direction
        if source_lang == "en":
            direction = "en-indic"
        elif target_lang == "en":
            direction = "indic-en"
        else:
            # Indic to Indic - translate via English
            return self._translate_via_english(text, source_lang, target_lang)

        # Load model if needed
        if not self.load_model(direction):
            return self._fallback_translation(text, source_lang, target_lang)

        try:
            model = self.models[direction]
            tokenizer = self.tokenizers[direction]

            # Prepare text with language tags
            if direction == "en-indic":
                input_text = f"<2{target_lang}> {text}"
            else:
                input_text = f"<2en> {text}"

            # Tokenize
            inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}

            # Generate translation
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    do_sample=False,
                    early_stopping=True
                )

            # Decode
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return {
                "translated_text": translated.strip(),
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence_score": 0.85,
                "model_used": f"IndicTrans2-{direction}"
            }

        except Exception as e:
            app_logger.error(f"Translation error: {e}")
            return self._fallback_translation(text, source_lang, target_lang)

    def _translate_via_english(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Translate between two Indic languages via English"""
        # First translate to English
        english_result = self.translate_text(text, source_lang, "en")
        if not english_result["translated_text"]:
            return self._fallback_translation(text, source_lang, target_lang)
        
        # Then translate from English to target
        final_result = self.translate_text(english_result["translated_text"], "en", target_lang)
        final_result["model_used"] = f"IndicTrans2-via-English"
        
        return final_result

    def _fallback_translation(self, text: str, source_lang: str, target_lang: str) -> Dict:
        """Fallback when models fail"""
        return {
            "translated_text": f"[Translation unavailable: {text}]",
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence_score": 0.1,
            "model_used": "fallback"
        }

    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[Dict]:
        """Translate multiple texts"""
        results = []
        for text in texts:
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
        return results


# Global instance
nlp_engine = SimpleNLPEngine()


def get_nlp_engine() -> SimpleNLPEngine:
    """Get the global NLP engine instance"""
    return nlp_engine