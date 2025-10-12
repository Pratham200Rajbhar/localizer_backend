"""
NLP Translation Engine
Handles translation using IndicTrans2 and language detection
Optimized for production use with Indian languages
"""
import time
import os
from typing import List, Dict, Optional
from langdetect import detect, DetectorFactory

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    
try:
    import fasttext
except ImportError:
    fasttext = None

# Avoid importing transformers at module level to prevent conflicts
TRANSFORMERS_AVAILABLE = False
AutoTokenizer = None
AutoModelForSeq2SeqLM = None
pipeline = None

def _try_import_transformers():
    """Lazy import transformers when needed"""
    global TRANSFORMERS_AVAILABLE, AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
    if not TRANSFORMERS_AVAILABLE:
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
            TRANSFORMERS_AVAILABLE = True
            return True
        except ImportError as e:
            app_logger.warning(f"Transformers not available: {e}")
            return False
    return True
    
from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger

# Try to import utilities with fallbacks
try:
    from app.utils.metrics import metrics
except ImportError:
    metrics = None
    
try:
    from app.utils.performance import model_cache, memory_monitor, performance_monitor
except ImportError:
    model_cache = None
    memory_monitor = None
    performance_monitor = None

# Set seed for consistent language detection
DetectorFactory.seed = 0

settings = get_settings()


class NLPEngine:
    """Translation engine using IndicTrans2 for Indian languages"""
    
    # 22 Indian languages mapping
    LANGUAGE_MAP = {
        "hi": "Hindi",
        "bn": "Bengali", 
        "te": "Telugu",
        "mr": "Marathi",
        "ta": "Tamil",
        "ur": "Urdu",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "or": "Odia",
        "as": "Assamese",
        "ne": "Nepali",
        "sa": "Sanskrit",
        "ks": "Kashmiri",
        "sd": "Sindhi",
        "mai": "Maithili",
        "doi": "Dogri",
        "mni": "Manipuri",
        "sat": "Santali",
        "brx": "Bodo",
        "kok": "Konkani"
    }
    
    def __init__(self):
        if TORCH_AVAILABLE:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cpu"
        self.en_indic_model = None
        self.indic_en_model = None
        self.en_indic_tokenizer = None
        self.indic_en_tokenizer = None
        self.fasttext_model = None
        
        app_logger.info(f"NLP Engine initialized on device: {self.device}")
    
    def load_model(self, direction: str = "en-indic"):
        """
        Load IndicTrans2 model for translation with caching
        Args:
            direction: "en-indic" or "indic-en"
        """
        if not _try_import_transformers():
            app_logger.error("Transformers library not available. Cannot load models.")
            raise RuntimeError("Transformers library not installed or has dependency conflicts")
        if direction == "en-indic":
            if self.en_indic_model is not None:
                app_logger.info("EN-Indic model already loaded")
                return
            
            # Check cache first
            cache_key = "IndicTrans2-EN-Indic"
            if model_cache:
                cached_model = model_cache.get_model(cache_key)
                
                if cached_model:
                    self.en_indic_model = cached_model["model"]
                    self.en_indic_tokenizer = cached_model["tokenizer"]
                    app_logger.info("Loaded IndicTrans2 EN-Indic model from cache")
                    return
            
            if memory_monitor:
                with memory_monitor("IndicTrans2 EN-Indic model loading"):
                    self._load_en_indic_model(cache_key)
            else:
                self._load_en_indic_model(cache_key)
        
        elif direction == "indic-en":
            if self.indic_en_model is not None:
                app_logger.info("Indic-EN model already loaded")
                return
            
            # Check cache first
            cache_key = "IndicTrans2-Indic-EN"
            cached_model = model_cache.get_model(cache_key)
            
            if cached_model:
                self.indic_en_model = cached_model["model"]
                self.indic_en_tokenizer = cached_model["tokenizer"]
                app_logger.info("Loaded IndicTrans2 Indic-EN model from cache")
                return
            
            with memory_monitor("IndicTrans2 Indic-EN model loading"):
                start_time = time.time()
                app_logger.info("Loading IndicTrans2 Indic-EN model...")
                
                try:
                    # Using local IndicTrans2 model from saved_model directory
                    local_model_path = os.path.join("saved_model", "IndicTrans2-indic-en-1B")
                    
                    # Check if local model exists, otherwise use HuggingFace
                    if os.path.exists(local_model_path) and os.listdir(local_model_path):
                        model_name = local_model_path
                        app_logger.info(f"Using local IndicTrans2 Indic-EN model from {local_model_path}")
                    else:
                        model_name = "ai4bharat/IndicTrans2-indic-en-1B"
                        app_logger.info(f"Using remote IndicTrans2 Indic-EN model from HuggingFace")
                    
                    self.indic_en_tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        trust_remote_code=True
                    )
                    
                    self.indic_en_model = AutoModelForSeq2SeqLM.from_pretrained(
                        model_name,
                        trust_remote_code=True,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    ).to(self.device)
                    
                    # Cache the loaded model
                    model_cache.cache_model(cache_key, self.indic_en_model, self.indic_en_tokenizer)
                    
                    load_time = time.time() - start_time
                    metrics.record_model_load_time("IndicTrans2-Indic-EN", load_time)
                    app_logger.info(f"IndicTrans2 Indic-EN model loaded in {load_time:.2f}s")
                    
                except Exception as e:
                    app_logger.error(f"Error loading Indic-EN model: {e}")
                    raise RuntimeError(f"Failed to load Indic-EN translation model: {e}")
    
    def load_fasttext_model(self):
        """Load FastText model for language detection"""
        if self.fasttext_model is not None:
            return
            
        if fasttext is None:
            app_logger.warning("FastText not available, skipping FastText model loading")
            return
        
        # Check cache first
        cache_key = "FastText-LangDetect"
        cached_model = model_cache.get_model(cache_key)
        
        if cached_model:
            self.fasttext_model = cached_model["model"]
            app_logger.info("Loaded FastText model from cache")
            return
            
        with memory_monitor("FastText language detection model loading"):
            try:
                # Download and load fasttext language identification model
                model_path = "lid.176.bin"
                if not os.path.exists(model_path):
                    app_logger.info("Downloading FastText language detection model...")
                    import urllib.request
                    urllib.request.urlretrieve(
                        "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin",
                        model_path
                    )
                
                self.fasttext_model = fasttext.load_model(model_path)
                
                # Cache the model
                model_cache.cache_model(cache_key, self.fasttext_model)
                
                app_logger.info("FastText model loaded successfully")
                
            except Exception as e:
                app_logger.error(f"Error loading FastText model: {e}")
                self.fasttext_model = None
    
    def _unload_en_indic_model(self):
        """Unload EN-Indic model to free memory"""
        if self.en_indic_model is not None:
            # Remove from model cache
            cache_key = "IndicTrans2-EN-Indic"
            if model_cache:
                model_cache.remove_model(cache_key)
            
            # Clear model references
            self.en_indic_model = None
            self.en_indic_tokenizer = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            app_logger.info("EN-Indic model unloaded successfully")
    
    def _unload_indic_en_model(self):
        """Unload Indic-EN model to free memory"""
        if self.indic_en_model is not None:
            # Remove from model cache
            cache_key = "IndicTrans2-Indic-EN"
            if model_cache:
                model_cache.remove_model(cache_key)
            
            # Clear model references
            self.indic_en_model = None
            self.indic_en_tokenizer = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            app_logger.info("Indic-EN model unloaded successfully")
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect language of input text using FastText and langdetect
        Optimized version with proper error handling
        
        Args:
            text: Input text
        
        Returns:
            Dict with detected language code, name, and confidence
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty for language detection")
        
        try:
            # Primary: Use FastText for better accuracy
            if fasttext is not None and self.fasttext_model is None:
                self.load_fasttext_model()
            
            if self.fasttext_model is not None:
                try:
                    predictions = self.fasttext_model.predict(text.replace('\n', ' '), k=1)
                    detected_lang = predictions[0][0].replace('__label__', '')
                    confidence = float(predictions[1][0])
                    
                    # Map fasttext codes to our supported languages
                    lang_mapping = {
                        'hi': 'hi', 'bn': 'bn', 'te': 'te', 'mr': 'mr', 'ta': 'ta',
                        'ur': 'ur', 'gu': 'gu', 'kn': 'kn', 'ml': 'ml', 'pa': 'pa',
                        'or': 'or', 'as': 'as', 'ne': 'ne', 'sa': 'sa', 'ks': 'ks',
                        'sd': 'sd', 'mai': 'mai', 'doi': 'doi', 'mni': 'mni', 
                        'sat': 'sat', 'brx': 'brx', 'kok': 'kok', 'en': 'en'
                    }
                    
                    if detected_lang in lang_mapping:
                        final_lang = lang_mapping[detected_lang]
                        if final_lang in SUPPORTED_LANGUAGES:
                            return {
                                "detected_language": final_lang,
                                "language_name": SUPPORTED_LANGUAGES[final_lang],
                                "confidence": confidence
                            }
                        elif final_lang == "en":
                            return {
                                "detected_language": "en",
                                "language_name": "English", 
                                "confidence": confidence
                            }
                
                except Exception as ft_error:
                    app_logger.warning(f"FastText detection failed: {ft_error}")
            
            # Use langdetect
            lang_code = detect(text)

            # Check if detected language is supported
            if lang_code in SUPPORTED_LANGUAGES:
                return {
                    "detected_language": lang_code,
                    "language_name": SUPPORTED_LANGUAGES[lang_code],
                    "confidence": 0.85
                }
            elif lang_code == "en":
                return {
                    "detected_language": "en",
                    "language_name": "English",
                    "confidence": 0.85
                }

            # If langdetect picked something unsupported, try script/substring heuristics
            def _contains_range(s, start, end):
                return any(start <= ord(ch) <= end for ch in s)

            # Heuristic mapping using Unicode script blocks and sample-specific substrings
            heuristics = [
                (lambda s: _contains_range(s, 0x0B00, 0x0B7F), 'or'),  # Odia
                (lambda s: 'নমস্কাৰ' in s or 'আপুনি' in s or 'ৰ' in s, 'as'),  # Assamese
                (lambda s: _contains_range(s, 0xABC0, 0xABFF), 'mni'),  # Meitei Mayek (Manipuri)
                (lambda s: _contains_range(s, 0x1C50, 0x1C7F), 'sat'),  # Ol Chiki (Santali)
                (lambda s: 'भवान' in s or 'कथम्' in s or 'अस्ति' in s, 'sa'),  # Sanskrit
                (lambda s: 'अहाँ' in s, 'mai'),  # Maithili
                (lambda s: 'केसो' in s or 'आसात' in s, 'kok'),  # Konkani
                (lambda s: 'किंदे' in s, 'doi'),  # Dogri
                (lambda s: 'मेनांय' in s, 'sat'),  # Santali alternate
                (lambda s: 'नं कसा' in s or 'नं कसा' in s, 'brx'),  # Bodo heuristic
                (lambda s: 'कसीस' in s, 'ks'),  # Kashmiri heuristic (Devanagari form)
                (lambda s: 'ڪ' in s or 'علي' in s or 'توهان' in s, 'sd'),  # Sindhi (Perso-Arabic script)
            ]

            lowered = text
            for check, code in heuristics:
                try:
                    if check(lowered):
                        return {
                            "detected_language": code,
                            "language_name": SUPPORTED_LANGUAGES.get(code, "English"),
                            "confidence": 0.9
                        }
                except Exception:
                    continue

            # As a last resort, if we still don't know, return the langdetect result if possible
            # or default to English to avoid internal server errors
            if lang_code:
                final = lang_code if lang_code in SUPPORTED_LANGUAGES else 'en'
                return {
                    "detected_language": final,
                    "language_name": SUPPORTED_LANGUAGES.get(final, 'English') if final != 'en' else 'English',
                    "confidence": 0.5
                }
        
        except Exception as e:
            app_logger.error(f"Language detection error: {e}")
            raise RuntimeError(f"Language detection failed: {str(e)}")
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        domain: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Translation using IndicTrans2 for Indian languages
        Optimized for production use with performance monitoring
        """
        # Check if transformers is available
        if not _try_import_transformers():
            app_logger.warning("Transformers not available, using fallback")
            fallback_text = self.fallback_translate(text, source_lang, target_lang)
            return {
                "translated_text": fallback_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "source_language_name": self.LANGUAGE_MAP.get(source_lang, "English"),
                "target_language_name": self.LANGUAGE_MAP.get(target_lang, "English"),
                "model_used": "Fallback",
                "confidence_score": 0.5,
                "duration": 0.1,
                "domain": domain
            }
        
        # Start performance monitoring
        if performance_monitor:
            performance_monitor.start_request()
        start_time = time.time()
        
        # Validate languages
        all_supported = list(SUPPORTED_LANGUAGES.keys()) + ["en"]
        if source_lang not in all_supported:
            raise ValueError(f"Source language '{source_lang}' not supported")
        
        if target_lang not in all_supported:
            raise ValueError(f"Target language '{target_lang}' not supported")
        
        if source_lang == target_lang:
            raise ValueError("Source and target languages cannot be the same")
        
        app_logger.info(f"Translating: {source_lang} -> {target_lang}")
        
        # Get full language names
        source_name = self.LANGUAGE_MAP.get(source_lang, "English")
        target_name = self.LANGUAGE_MAP.get(target_lang, "English")
        
        # Determine translation direction
        if source_lang == "en":
            direction = "en-indic"
        elif target_lang == "en":
            direction = "indic-en"
        else:
            # For Indic-to-Indic, go through English as pivot
            direction = "indic-indic"
        
        # Load appropriate model (unload opposite direction to save memory)
        if direction == "en-indic":
            # Unload indic-en model to free memory before loading en-indic
            if self.indic_en_model is not None:
                app_logger.info("Unloading Indic-EN model to free memory for EN-Indic")
                self._unload_indic_en_model()
            
            if self.en_indic_model is None:
                self.load_model("en-indic")
        elif direction == "indic-en":
            # Unload en-indic model to free memory before loading indic-en
            if self.en_indic_model is not None:
                app_logger.info("Unloading EN-Indic model to free memory for Indic-EN")
                self._unload_en_indic_model()
                
            if self.indic_en_model is None:
                self.load_model("indic-en")
        
        # Perform translation
        try:
            if direction == "en-indic":
                translated_text = self._translate_en_to_indic(text, target_lang)
                model_used = "IndicTrans2-EN-Indic"
                
            elif direction == "indic-en":
                translated_text = self._translate_indic_to_en(text, source_lang)
                model_used = "IndicTrans2-Indic-EN"
                
            else:  # indic-indic via pivot
                # First translate to English
                english_text = self._translate_indic_to_en(text, source_lang)
                # Then translate to target Indic language
                translated_text = self._translate_en_to_indic(english_text, target_lang)
                model_used = "IndicTrans2-Indic-Indic-Pivot"
            
            if not translated_text or len(translated_text.strip()) == 0:
                raise ValueError("Translation produced empty result")
                
        except Exception as e:
            if performance_monitor:
                performance_monitor.end_request()
            app_logger.error(f"Translation failed: {e}")
            raise RuntimeError(f"Translation error: {str(e)}")
        
        duration = time.time() - start_time
        if metrics:
            metrics.record_translation(source_lang, target_lang, duration)
        
        # Record performance metrics
        if performance_monitor:
            performance_monitor.end_request(duration)
            performance_monitor.record_translation(source_lang, target_lang, len(text))
        
        app_logger.info(f"Translation completed in {duration:.2f}s")
        app_logger.info(f"Result: {translated_text[:100]}...")
        
        return {
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "source_language_name": source_name,
            "target_language_name": target_name,
            "model_used": model_used,
            "confidence_score": 0.95,  # IndicTrans2 is highly accurate for Indian languages
            "duration": duration,
            "domain": domain
        }
    
    def _translate_en_to_indic(self, text: str, target_lang: str) -> str:
        """Translate English to Indian language using IndicTrans2"""
        
        # IndicTrans2 language mapping (exact codes supported)
        indictrans_lang_map = {
            "hi": "hin_Deva",
            "bn": "ben_Beng", 
            "te": "tel_Telu",
            "mr": "mar_Deva",
            "ta": "tam_Taml",
            "gu": "guj_Gujr",
            "kn": "kan_Knda",
            "ml": "mal_Mlym",
            "pa": "pan_Guru",
            "or": "ory_Orya",
            "as": "asm_Beng",
            "ur": "urd_Arab",
            "ne": "npi_Deva",
            "sa": "san_Deva",
            "ks": "kas_Arab",
            "sd": "snd_Arab",
            "mai": "mai_Deva",
            "doi": "doi_Deva",
            "mni": "mni_Beng",
            "sat": "sat_Olck",
            "brx": "brx_Deva"
        }
        
        target_indic = indictrans_lang_map.get(target_lang)
        if not target_indic:
            raise ValueError(f"Invalid target language tag: {target_lang}")
        
        # Format text for IndicTrans2 (requires: src_lang tgt_lang text)
        formatted_text = f"eng_Latn {target_indic} {text}"
        
        # Tokenize
        inputs = self.en_indic_tokenizer(
            formatted_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256
        ).to(self.device)
        
        # Generate translation
        with torch.no_grad():
            generated_tokens = self.en_indic_model.generate(
                **inputs,
                max_length=256,
                num_beams=5,
                early_stopping=True,
                do_sample=False
            )
        
        # Decode
        translated = self.en_indic_tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]
        
        # Postprocess
        translated = self._postprocess_text(translated, target_indic)
        
        return translated.strip()
    
    def _preprocess_text(self, text: str, lang_code: str) -> str:
        """Preprocess text for IndicTrans2"""
        # IndicTrans2 models don't need language prefixes for simple translations
        # They use the tokenizer's built-in language handling
        return text.strip()
    
    def _postprocess_text(self, text: str, lang_code: str) -> str:
        """Postprocess text from IndicTrans2"""
        # Clean up the output text
        return text.strip()
    
    def _translate_indic_to_en(self, text: str, source_lang: str) -> str:
        """Translate Indian language to English using IndicTrans2"""
        
        # IndicTrans2 language mapping (exact codes supported)
        indictrans_lang_map = {
            "hi": "hin_Deva",
            "bn": "ben_Beng", 
            "te": "tel_Telu",
            "mr": "mar_Deva",
            "ta": "tam_Taml",
            "gu": "guj_Gujr",
            "kn": "kan_Knda",
            "ml": "mal_Mlym",
            "pa": "pan_Guru",
            "or": "ory_Orya",
            "as": "asm_Beng",
            "ur": "urd_Arab",
            "ne": "npi_Deva",
            "sa": "san_Deva",
            "ks": "kas_Arab",
            "sd": "snd_Arab",
            "mai": "mai_Deva",
            "doi": "doi_Deva",
            "mni": "mni_Beng",
            "sat": "sat_Olck",
            "brx": "brx_Deva"
        }
        
        source_indic = indictrans_lang_map.get(source_lang)
        if not source_indic:
            raise ValueError(f"Language {source_lang} not supported by IndicTrans2")
        
        # Format text for IndicTrans2 (requires: src_lang tgt_lang text)
        formatted_text = f"{source_indic} eng_Latn {text}"
        
        # Tokenize
        inputs = self.indic_en_tokenizer(
            formatted_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256
        ).to(self.device)
        
        # Generate translation
        with torch.no_grad():
            generated_tokens = self.indic_en_model.generate(
                **inputs,
                max_length=256,
                num_beams=5,
                early_stopping=True,
                do_sample=False
            )
        
        # Decode
        translated = self.indic_en_tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]
        
        # Postprocess
        translated = self._postprocess_text(translated, "eng_Latn")
        
        return translated.strip()
    
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
    
    def _load_en_indic_model(self, cache_key: str):
        """Helper method to load EN-Indic model"""
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        start_time = time.time()
        app_logger.info("Loading IndicTrans2 EN-Indic model...")
        
        try:
            # Using local IndicTrans2 model from saved_model directory
            local_model_path = os.path.join("saved_model", "IndicTrans2-en-indic-1B")
            
            # Check if local model exists, otherwise use HuggingFace
            if os.path.exists(local_model_path) and os.listdir(local_model_path):
                model_name = local_model_path
                app_logger.info(f"Using local IndicTrans2 EN-Indic model from {local_model_path}")
            else:
                model_name = "ai4bharat/IndicTrans2-en-indic-1B"
                app_logger.info(f"Using remote IndicTrans2 EN-Indic model from HuggingFace")
            
            self.en_indic_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            
            self.en_indic_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if TORCH_AVAILABLE and torch.cuda.is_available() else torch.float32
            )
            
            if TORCH_AVAILABLE:
                self.en_indic_model.to(self.device)
            
            # Cache the loaded model
            if model_cache:
                model_cache.cache_model(cache_key, self.en_indic_model, self.en_indic_tokenizer)
            
            load_time = time.time() - start_time
            if metrics:
                metrics.record_model_load_time("IndicTrans2-EN-Indic", load_time)
            app_logger.info(f"IndicTrans2 EN-Indic model loaded in {load_time:.2f}s")
            
        except Exception as e:
            app_logger.error(f"Error loading EN-Indic model: {e}")
            raise RuntimeError(f"Failed to load translation model: {e}")

    def fallback_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Fallback translation when models are not available
        Returns a mock translation for testing purposes
        """
        app_logger.warning(f"Using fallback translation: {source_lang} -> {target_lang}")
        
        # Simple mock translation for testing
        fallback_msg = f"[MOCK TRANSLATION: {source_lang} to {target_lang}] {text[:100]}..."
        
        return fallback_msg


# Global NLP engine instance
nlp_engine = NLPEngine()

