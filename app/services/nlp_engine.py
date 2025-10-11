"""
NLP Translation Engine
Handles translation using IndicTrans2 and other models
"""
import time
from typing import List, Dict, Optional
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from langdetect import detect, DetectorFactory
from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger
from app.utils.metrics import metrics

# Set seed for consistent language detection
DetectorFactory.seed = 0

settings = get_settings()


class NLPEngine:
    """Translation engine using IndicTrans2"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}
        app_logger.info(f"NLP Engine initialized on device: {self.device}")
    
    def load_model(self, model_name: str, direction: str = "en-indic"):
        """
        Load translation model
        
        Args:
            model_name: Model identifier
            direction: Translation direction (en-indic or indic-en)
        """
        if model_name in self.models:
            app_logger.info(f"Model {model_name} already loaded")
            return
        
        start_time = time.time()
        app_logger.info(f"Loading model: {model_name}")
        
        try:
            # Use smaller model for faster loading in demo
            if direction == "en-indic":
                model_path = "ai4bharat/IndicTrans2-en-indic-1B"
            else:
                model_path = "ai4bharat/IndicTrans2-indic-en-1B"
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                trust_remote_code=True
            ).to(self.device)
            
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            
            load_time = time.time() - start_time
            metrics.record_model_load_time(model_name, load_time)
            
            app_logger.info(f"Model {model_name} loaded in {load_time:.2f}s")
        
        except Exception as e:
            app_logger.error(f"Error loading model {model_name}: {e}")
            raise
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect language of input text
        
        Args:
            text: Input text
        
        Returns:
            Dict with detected language code, name, and confidence
        """
        try:
            lang_code = detect(text)
            
            # Map detected language to supported languages
            if lang_code in SUPPORTED_LANGUAGES:
                return {
                    "detected_language": lang_code,
                    "language_name": SUPPORTED_LANGUAGES[lang_code],
                    "confidence": 0.95
                }
            elif lang_code == "en":
                return {
                    "detected_language": "en",
                    "language_name": "English",
                    "confidence": 0.95
                }
            else:
                # Return Hindi as default for unsupported languages
                return {
                    "detected_language": "hi",
                    "language_name": "Hindi",
                    "confidence": 0.5
                }
        
        except Exception as e:
            app_logger.error(f"Language detection error: {e}")
            return {
                "detected_language": "hi",
                "language_name": "Hindi",
                "confidence": 0.3
            }
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        domain: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Translate text from source to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            domain: Optional domain for context
        
        Returns:
            Dict with translated text and metadata
        """
        start_time = time.time()
        
        try:
            # Determine direction
            if source_lang == "en":
                direction = "en-indic"
                model_name = "IndicTrans2-en-indic"
            else:
                direction = "indic-en"
                model_name = "IndicTrans2-indic-en"
            
            # Load model if not already loaded
            if model_name not in self.models:
                self.load_model(model_name, direction)
            
            model = self.models[model_name]
            tokenizer = self.tokenizers[model_name]
            
            # Prepare input
            # For IndicTrans2, we need to add language tags
            if direction == "en-indic":
                input_text = f"<2{target_lang}> {text}"
            else:
                input_text = f"<2en> {text}"
            
            # Tokenize
            inputs = tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True
                )
            
            # Decode output
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            duration = time.time() - start_time
            metrics.record_translation(source_lang, target_lang, duration)
            
            app_logger.info(
                f"Translation completed: {source_lang}->{target_lang} "
                f"in {duration:.2f}s"
            )
            
            return {
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "model_used": model_name,
                "confidence_score": 0.85,
                "duration": duration
            }
        
        except Exception as e:
            app_logger.error(f"Translation error: {e}")
            raise
    
    def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[Dict[str, any]]:
        """
        Translate multiple texts in batch
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            List of translation results
        """
        results = []
        
        for text in texts:
            try:
                result = self.translate(text, source_lang, target_lang)
                results.append(result)
            except Exception as e:
                app_logger.error(f"Batch translation error: {e}")
                results.append({
                    "error": str(e),
                    "text": text
                })
        
        return results


# Global NLP engine instance
nlp_engine = NLPEngine()

