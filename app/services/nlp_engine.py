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
    
    # IndicTrans2 language code mapping
    INDIC_TRANS_LANG_MAP = {
        "en": "eng_Latn",
        "hi": "hin_Deva",
        "bn": "ben_Beng", 
        "te": "tel_Telu",
        "mr": "mar_Deva",
        "ta": "tam_Taml",
        "ur": "urd_Arab",
        "gu": "guj_Gujr",
        "kn": "kan_Knda",
        "ml": "mal_Mlym",
        "pa": "pan_Guru",
        "or": "ori_Orya",
        "as": "asm_Beng",
        "ne": "nep_Deva",
        "sa": "san_Deva",
        "ks": "kas_Arab",
        "sd": "snd_Arab",
        "mai": "mai_Deva",
        "bh": "bho_Deva",
        "gom": "gom_Deva",
        "doi": "doi_Deva",
        "mni": "mni_Mtei",
        "sat": "sat_Olck"
    }
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}
        
        # Initialize IndicProcessor for IndicTrans2
        try:
            from IndicTransToolkit.processor import IndicProcessor
            self.indic_processor = IndicProcessor(inference=True)
            app_logger.info("IndicProcessor initialized successfully")
        except ImportError as e:
            app_logger.error(f"Failed to import IndicTransToolkit: {e}")
            self.indic_processor = None
        
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
            # Use IndicTrans2 models as specified in prompt.mdc
            if direction == "en-indic":
                model_path = "ai4bharat/indictrans2-en-indic-dist-200M"
            else:
                model_path = "ai4bharat/indictrans2-indic-en-dist-200M"
            
            app_logger.info(f"Loading model from: {model_path}")
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                revision="main",
                use_fast=False
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                revision="main"
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
        
        Raises:
            ValueError: If detected language is not supported
        """
        try:
            lang_code = detect(text)
            
            # Check if detected language is supported
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
                # Raise error for unsupported languages - no fallback
                raise ValueError(
                    f"Detected language '{lang_code}' is not supported. "
                    f"Only 22 Indian languages and English are supported."
                )
        
        except Exception as e:
            app_logger.error(f"Language detection error: {e}")
            raise RuntimeError(f"Language detection failed: {e}")
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        domain: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Clean translation implementation using IndicTrans2
        """
        start_time = time.time()
        
        # Basic validation
        if source_lang not in SUPPORTED_LANGUAGES and source_lang != "en":
            raise ValueError(f"Source language '{source_lang}' not supported")
        
        if target_lang not in SUPPORTED_LANGUAGES and target_lang != "en":
            raise ValueError(f"Target language '{target_lang}' not supported")
        
        if source_lang == target_lang:
            raise ValueError("Source and target languages cannot be the same")
        
        # Determine model direction
        if source_lang == "en" and target_lang in SUPPORTED_LANGUAGES:
            model_name = "IndicTrans2-en-indic"
            direction = "en-indic"
        elif source_lang in SUPPORTED_LANGUAGES and target_lang == "en":
            model_name = "IndicTrans2-indic-en"  
            direction = "indic-en"
        else:
            raise ValueError(f"Translation between {source_lang} and {target_lang} not supported")
        
        # Load model
        if model_name not in self.models:
            self.load_model(model_name, direction)
        
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        
        app_logger.info(f"Translating with {model_name}: {source_lang} -> {target_lang}")
        
        if self.indic_processor is None:
            raise ValueError("IndicProcessor not initialized")
        
        # Convert language codes to IndicTrans2 format
        src_lang_code = "eng_Latn" if source_lang == "en" else self.INDIC_TRANS_LANG_MAP.get(source_lang)
        tgt_lang_code = "eng_Latn" if target_lang == "en" else self.INDIC_TRANS_LANG_MAP.get(target_lang)
        
        if not src_lang_code or not tgt_lang_code:
            raise ValueError(f"Unsupported language mapping: {source_lang} -> {target_lang}")
        
        app_logger.info(f"Language mapping: {source_lang} ({src_lang_code}) -> {target_lang} ({tgt_lang_code})")
        
        # Preprocess with IndicProcessor
        app_logger.info("Starting preprocessing...")
        batch = self.indic_processor.preprocess_batch([text.strip()], src_lang=src_lang_code, tgt_lang=tgt_lang_code)
        app_logger.info(f"Preprocessing complete. Processed text: {batch[0][:100]}...")
        
        # Tokenize
        app_logger.info("Starting tokenization...")
        inputs = tokenizer(
            batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(self.device)
        app_logger.info(f"Tokenization complete. Input shape: {inputs['input_ids'].shape}")
        
        # Generate
        app_logger.info("Starting generation...")
        try:
            with torch.no_grad():
                outputs = model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    use_cache=False,  # Disable caching to avoid past_key_values bug in IndicTrans2
                    min_length=0,
                    max_length=256,
                    num_beams=5,
                    num_return_sequences=1,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            
            if outputs is None:
                raise ValueError("Model generation returned None")
                
            app_logger.info(f"Generation complete. Output shape: {outputs.shape}")
            
        except Exception as e:
            app_logger.error(f"Generation failed: {e}")
            app_logger.info(f"Input details: {inputs}")
            app_logger.info(f"Model type: {type(model)}")
            raise
        
        # Decode
        app_logger.info("Starting decoding...")
        generated_tokens = tokenizer.batch_decode(
            outputs,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        app_logger.info(f"Decoding complete. Generated tokens: {generated_tokens}")
        
        # Postprocess with IndicProcessor
        app_logger.info("Starting postprocessing...")
        translations = self.indic_processor.postprocess_batch(generated_tokens, lang=tgt_lang_code)
        translated_text = translations[0].strip()
        app_logger.info(f"Decoding complete. Result: {translated_text}")
        
        duration = time.time() - start_time
        
        app_logger.info(f"Translation completed in {duration:.2f}s")
        
        return {
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "source_language_name": SUPPORTED_LANGUAGES.get(source_lang, "English"),
            "target_language_name": SUPPORTED_LANGUAGES.get(target_lang, "English"),
            "model_used": model_name,
            "confidence_score": 0.90,
            "duration": duration,
            "domain": domain
        }
    
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

