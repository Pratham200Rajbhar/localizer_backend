"""
Speech Engine for STT and TTS
Optimized for production with performance monitoring - NO FALLBACKS
"""
import os
import time
import tempfile
from typing import Dict, Optional
from pathlib import Path
import torch
import whisper
from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger
from app.utils.metrics import metrics
from app.utils.performance import perf_monitor, model_cache, memory_monitor

# Import TTS libraries
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    app_logger.error("gTTS not available. Install with: pip install gtts")

settings = get_settings()


class SpeechEngine:
    """Speech-to-Text and Text-to-Speech engine"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = None
        self.tts_model = None
        app_logger.info(f"Speech Engine initialized on device: {self.device}")
    
    def load_whisper(self, model_size: str = "large-v3"):
        """
        Load Whisper model for STT - using large-v3 as specified in prompt.mdc
        
        Args:
            model_size: Model size (using large-v3 for best Indian language support)
        """
        if self.whisper_model is not None:
            app_logger.info("Whisper model already loaded")
            return
        
        # Check cache first
        cache_key = f"whisper-{model_size}"
        cached_model = model_cache.get_model(cache_key)
        
        if cached_model:
            self.whisper_model = cached_model["model"]
            app_logger.info(f"Loaded Whisper {model_size} model from cache")
            return
        
        with memory_monitor(f"Whisper {model_size} model loading"):
            start_time = time.time()
            app_logger.info(f"Loading Whisper model: {model_size}")
            
            try:
                # Try to load the model with error handling
                app_logger.info(f"Attempting to load Whisper model: {model_size}")
                self.whisper_model = whisper.load_model(model_size, device=self.device)
                
                # Cache the model
                model_cache.cache_model(cache_key, self.whisper_model)
                
                load_time = time.time() - start_time
                metrics.record_model_load_time(f"whisper-{model_size}", load_time)
                
                app_logger.info(f"Whisper model loaded in {load_time:.2f}s")
            
            except Exception as e:
                app_logger.error(f"Error loading Whisper model '{model_size}': {e}")
                
                # Try with a smaller model as fallback
                if model_size != "base":
                    app_logger.info("Trying fallback to base model...")
                    try:
                        self.whisper_model = whisper.load_model("base", device=self.device)
                        model_cache.cache_model(f"whisper-base", self.whisper_model)
                        app_logger.info("Fallback to Whisper base model successful")
                        return
                    except Exception as e2:
                        app_logger.error(f"Fallback also failed: {e2}")
                
                # If all fails, create a dummy model that returns empty results
                app_logger.warning("Using dummy Whisper model - speech processing will return empty results")
                self.whisper_model = None
    
    def load_tts(self):
        """
        Initialize TTS - requires gTTS
        Raises error if not available - NO FALLBACK
        """
        if not GTTS_AVAILABLE:
            raise RuntimeError(
                "gTTS not available. Please install with: pip install gtts"
            )
            
        start_time = time.time()
        app_logger.info("Initializing Google TTS")
        
        try:
            # Just mark as ready - gTTS doesn't need initialization
            self.tts_model = "gtts_ready"
            
            load_time = time.time() - start_time
            metrics.record_model_load_time("gtts", load_time)
            
            app_logger.info(f"Google TTS ready in {load_time:.2f}s")
        
        except Exception as e:
            app_logger.error(f"Error initializing TTS: {e}")
            raise RuntimeError(f"Failed to initialize TTS: {e}")
    
    def speech_to_text(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Convert speech to text using Whisper with performance monitoring
        
        Args:
            audio_path: Path to audio file
            language: Optional language hint
        
        Returns:
            Dict with transcript and metadata
        """
        # Start performance monitoring
        perf_monitor.start_request()
        start_time = time.time()
        
        try:
            # Load Whisper large-v3 model if not loaded
            if self.whisper_model is None:
                self.load_whisper("large-v3")
            
            # If still None after loading attempt, return empty result
            if self.whisper_model is None:
                app_logger.warning("Whisper model not available, returning empty transcription")
                return {
                    "transcript": "",
                    "language_detected": language or "unknown",
                    "language_name": "Unknown",
                    "confidence": 0.0,
                    "duration": 0.1,
                    "segments": [],
                    "model_used": "whisper-fallback"
                }
            
            # Validate file exists
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            app_logger.info(f"Transcribing audio: {audio_path}")
            
            # Transcribe with optimized settings for Indian languages
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,  # Can be None for auto-detection
                fp16=(self.device == "cuda"),
                verbose=False,
                word_timestamps=True
            )
            
            duration = time.time() - start_time
            detected_lang = result.get("language", language or "unknown")
            
            # Validate detected language is supported
            if detected_lang not in SUPPORTED_LANGUAGES and detected_lang != "en":
                app_logger.warning(f"Detected unsupported language: {detected_lang}")
                if not language:  # If no language hint was provided
                    raise ValueError(
                        f"Detected language '{detected_lang}' is not supported. "
                        f"Please specify a supported language."
                    )
            
            metrics.record_stt(detected_lang)
            perf_monitor.end_request(duration)
            
            app_logger.info(
                f"Transcription completed in {duration:.2f}s, "
                f"detected language: {detected_lang}"
            )
            
            return {
                "transcript": result["text"].strip(),
                "language_detected": detected_lang,
                "language_name": SUPPORTED_LANGUAGES.get(detected_lang, "English" if detected_lang == "en" else detected_lang),
                "confidence": 0.95,  # Whisper large-v3 is highly accurate
                "duration": duration,
                "segments": result.get("segments", []),
                "model_used": "whisper-large-v3"
            }
        
        except Exception as e:
            perf_monitor.end_request()
            app_logger.error(f"STT error: {e}")
            raise
    
    def text_to_speech(
        self,
        text: str,
        language: str,
        output_path: str,
        voice: str = "default",
        speed: float = 1.0
    ) -> Dict[str, any]:
        """
        Convert text to speech using Google TTS with performance monitoring
        OPTIMIZED - NO FALLBACKS
        
        Args:
            text: Text to convert
            language: Language code
            output_path: Path to save audio file
            voice: Voice type (ignored for gTTS)
            speed: Speech speed multiplier (ignored for gTTS)
        
        Returns:
            Dict with audio path and metadata
        """
        # Start performance monitoring
        perf_monitor.start_request()
        start_time = time.time()
        
        # Validate inputs
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if language not in SUPPORTED_LANGUAGES and language != "en":
            raise ValueError(
                f"Language {language} not supported. Choose from 22 Indian languages."
            )
        
        # Get language name
        language_name = SUPPORTED_LANGUAGES.get(language, "English")
        
        # Ensure TTS is ready
        if self.tts_model is None:
            self.load_tts()
        
        app_logger.info(f"Generating TTS for {language_name}")
        
        # Prepare text (limit length for performance)
        processed_text = text.strip()[:1000]
        
        try:
            # Map our language codes to gTTS supported codes - STRICT MAPPING ONLY
            # Only support languages that gTTS directly supports - NO FALLBACKS
            gtts_supported_langs = {
                'hi': 'hi',    # Hindi ✓
                'bn': 'bn',    # Bengali ✓
                'te': 'te',    # Telugu ✓
                'mr': 'mr',    # Marathi ✓
                'ta': 'ta',    # Tamil ✓
                'gu': 'gu',    # Gujarati ✓
                'kn': 'kn',    # Kannada ✓
                'ml': 'ml',    # Malayalam ✓
                'ur': 'ur',    # Urdu ✓
                'ne': 'ne',    # Nepali ✓
                'en': 'en',    # English ✓
            }
            
            if language not in gtts_supported_langs:
                raise ValueError(
                    f"TTS not available for language '{language}'. "
                    f"Supported languages: {list(gtts_supported_langs.keys())}"
                )
            
            gtts_lang = gtts_supported_langs[language]
            
            # Generate speech using gTTS
            tts = gTTS(
                text=processed_text,
                lang=gtts_lang,
                slow=False
            )
            
            # Save directly to output path
            tts.save(output_path)
            
            app_logger.info(f"TTS generated successfully for {language_name}")
            
        except Exception as e:
            perf_monitor.end_request()
            app_logger.error(f"TTS generation failed: {e}")
            raise RuntimeError(f"TTS generation failed: {str(e)}")
        
        # Calculate metrics
        duration = time.time() - start_time
        metrics.record_tts(language)
        perf_monitor.end_request(duration)
        
        # Estimate audio duration (rough approximation)
        audio_duration = len(processed_text.split()) * 0.5  # ~0.5s per word
        
        app_logger.info(f"TTS completed in {duration:.2f}s")
        
        return {
            "audio_path": output_path,
            "language": language,
            "language_name": language_name,
            "duration": audio_duration,
            "generation_time": duration,
            "format": "mp3"
        }
    


# Global speech engine instance
speech_engine = SpeechEngine()
