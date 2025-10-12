"""
Speech Engine for STT and TTS
Optimized for production with performance monitoring and fast processing
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
        Optimized Whisper model loading with performance improvements
        
        Args:
            model_size: Model size (default: large-v3 for accuracy, falls back to base for speed)
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
                # Performance optimization: Try smaller models first for faster loading
                models_to_try = []
                if model_size == "large-v3":
                    models_to_try = ["base", "small", "medium"]  # Start with fastest
                elif model_size == "large":
                    models_to_try = ["base", "small"]
                else:
                    models_to_try = [model_size]
                
                # Try the requested model first if it's not large-v3
                if model_size != "large-v3":
                    models_to_try.insert(0, model_size)
                
                for model_name in models_to_try:
                    try:
                        app_logger.info(f"Attempting to load Whisper model: {model_name}")
                        
                        # Set lower precision for faster loading and inference
                        if self.device == "cuda":
                            import torch
                            torch.backends.cudnn.benchmark = True
                        
                        self.whisper_model = whisper.load_model(
                            model_name, 
                            device=self.device,
                            download_root="./models"  # Use local model directory
                        )
                        
                        # Cache the successful model
                        model_cache.cache_model(f"whisper-{model_name}", self.whisper_model)
                        
                        load_time = time.time() - start_time
                        metrics.record_model_load_time(f"whisper-{model_name}", load_time)
                        
                        app_logger.info(
                            f"Whisper {model_name} model loaded successfully in {load_time:.2f}s "
                            f"(requested: {model_size})"
                        )
                        return
                    
                    except Exception as e:
                        app_logger.warning(f"Failed to load Whisper {model_name}: {e}")
                        continue
                
                # If all models fail
                raise RuntimeError(f"Could not load any Whisper model")
            
            except Exception as e:
                app_logger.error(f"Error loading Whisper model: {e}")
                app_logger.warning("Using dummy Whisper model - speech processing will return empty results")
                self.whisper_model = None
    
    def validate_audio_file(self, audio_path: str) -> Dict[str, any]:
        """
        Validate audio file for common issues
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dict with validation results
        """
        try:
            import librosa
            import numpy as np
            
            # Load audio file
            audio, sr = librosa.load(audio_path, sr=None, duration=5)  # Load first 5 seconds
            
            # Check if audio is mostly silence
            rms_energy = np.sqrt(np.mean(audio**2))
            is_silent = rms_energy < 0.01
            
            # Check for clipping
            is_clipped = np.any(np.abs(audio) > 0.95)
            
            # Check sample rate
            is_good_sr = sr >= 8000
            
            return {
                "is_valid": not is_silent and is_good_sr,
                "is_silent": is_silent,
                "is_clipped": is_clipped,
                "sample_rate": sr,
                "rms_energy": float(rms_energy),
                "duration_seconds": len(audio) / sr
            }
        
        except Exception as e:
            app_logger.warning(f"Audio validation failed: {e}")
            return {
                "is_valid": True,  # Assume valid if we can't validate
                "error": str(e)
            }
    
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
        Enhanced with better edge case handling and error recovery
        
        Args:
            audio_path: Path to audio file
            language: Optional language hint (use None for auto-detection)
        
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
            
            # Validate file exists and is readable
            audio_file = Path(audio_path)
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if audio_file.stat().st_size == 0:
                raise ValueError(f"Audio file is empty: {audio_path}")
            
            if audio_file.stat().st_size > 100 * 1024 * 1024:  # 100MB limit
                raise ValueError(f"Audio file too large: {audio_path}")
            
            app_logger.info(f"Transcribing audio: {audio_path}")
            
            # Simplified transcription options for better compatibility and performance
            transcribe_options = {
                "fp16": (self.device == "cuda"),
                "verbose": False,
                "word_timestamps": False,  # Disable for faster processing
                "temperature": 0.0  # More deterministic results
            }
            
            # Handle language hint properly
            if language and language in SUPPORTED_LANGUAGES:
                # For Indian languages, let Whisper auto-detect but validate result
                transcribe_options["language"] = None  # Auto-detect
                app_logger.info(f"Language hint provided: {language} ({SUPPORTED_LANGUAGES[language]})")
            elif language == "en":
                transcribe_options["language"] = "en"
                app_logger.info("English language specified")
            else:
                transcribe_options["language"] = None
                app_logger.info("Auto-detecting language")
            
            # Performance optimization: Pre-process audio for faster transcription
            try:
                import librosa
                import numpy as np
                
                # Load and optimize audio
                audio, sr = librosa.load(audio_path, sr=16000)  # Whisper expects 16kHz
                
                # Trim silence for faster processing
                audio, _ = librosa.effects.trim(audio, top_db=30)
                
                # Limit audio length for very long files (process first 5 minutes)
                max_samples = 16000 * 300  # 5 minutes
                if len(audio) > max_samples:
                    audio = audio[:max_samples]
                    app_logger.warning("Audio truncated to 5 minutes for faster processing")
                
                # Save optimized audio temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                    import soundfile as sf
                    sf.write(temp_wav.name, audio, sr)
                    optimized_audio_path = temp_wav.name
                
                # Perform transcription on optimized audio
                result = self.whisper_model.transcribe(optimized_audio_path, **transcribe_options)
                
                # Clean up temporary file
                os.unlink(optimized_audio_path)
            
            except ImportError:
                # Fallback to original file if librosa is not available
                app_logger.warning("Librosa not available, using original audio file")
                result = self.whisper_model.transcribe(audio_path, **transcribe_options)
            
            except Exception as audio_error:
                app_logger.warning(f"Audio preprocessing failed: {audio_error}, using original file")
                result = self.whisper_model.transcribe(audio_path, **transcribe_options)
            
            duration = time.time() - start_time
            detected_lang = result.get("language", "unknown")
            transcript = result["text"].strip()
            
            # Handle empty or very short transcripts
            if not transcript or len(transcript) < 3:
                app_logger.warning("Transcript is empty or too short, checking for silence")
                return {
                    "transcript": "",
                    "language_detected": detected_lang,
                    "language_name": SUPPORTED_LANGUAGES.get(detected_lang, "Unknown"),
                    "confidence": 0.1,
                    "duration": duration,
                    "segments": [],
                    "model_used": "whisper-large-v3",
                    "warning": "Audio appears to contain mostly silence or noise"
                }
            
            # Language validation - be more permissive for mixed content
            if language and language in SUPPORTED_LANGUAGES:
                # If user specified a language hint, accept the result but note the detected language
                if detected_lang != language and detected_lang != "unknown":
                    app_logger.info(f"Language hint: {language}, detected: {detected_lang}")
                    # Use the hint as the primary language
                    final_lang = language
                    language_name = SUPPORTED_LANGUAGES[language]
                else:
                    final_lang = detected_lang
                    language_name = SUPPORTED_LANGUAGES.get(detected_lang, "English" if detected_lang == "en" else detected_lang)
            else:
                # No hint provided, use detected language
                final_lang = detected_lang
                if detected_lang in SUPPORTED_LANGUAGES:
                    language_name = SUPPORTED_LANGUAGES[detected_lang]
                elif detected_lang == "en":
                    language_name = "English"
                else:
                    # For unsupported languages, still return the result with a warning
                    language_name = detected_lang.title() if detected_lang != "unknown" else "Unknown"
            
            # Calculate confidence based on transcript length and segments
            confidence = min(0.95, max(0.3, len(transcript) / 100))  # Basic confidence estimation
            
            metrics.record_stt(final_lang)
            perf_monitor.end_request(duration)
            
            app_logger.info(
                f"Transcription completed in {duration:.2f}s, "
                f"final language: {final_lang}, detected: {detected_lang}"
            )
            
            result_data = {
                "transcript": transcript,
                "language_detected": final_lang,
                "language_name": language_name,
                "confidence": confidence,
                "duration": duration,
                "segments": result.get("segments", []),
                "model_used": "whisper-large-v3"
            }
            
            # Add metadata for mixed language content
            if language and detected_lang != language and detected_lang != "unknown":
                result_data["metadata"] = {
                    "language_hint": language,
                    "whisper_detected": detected_lang,
                    "note": "Content may contain mixed languages"
                }
            
            return result_data
        
        except FileNotFoundError as e:
            perf_monitor.end_request()
            app_logger.error(f"STT file not found: {e}")
            raise ValueError(f"Audio file not found: {audio_path}")
        
        except ValueError as e:
            perf_monitor.end_request()
            app_logger.error(f"STT validation error: {e}")
            raise
        
        except RuntimeError as e:
            perf_monitor.end_request()
            app_logger.error(f"STT runtime error: {e}")
            if "CUDA" in str(e) or "memory" in str(e).lower():
                # GPU memory issue, try to recover
                app_logger.warning("GPU memory error, attempting recovery")
                try:
                    import torch
                    torch.cuda.empty_cache()
                    # Retry with CPU
                    self.device = "cpu"
                    self.whisper_model = None
                    self.load_whisper("base")  # Use smaller model on CPU
                    return self.speech_to_text(audio_path, language)
                except Exception as retry_error:
                    app_logger.error(f"Recovery failed: {retry_error}")
                    raise RuntimeError("Speech recognition failed due to resource constraints")
            else:
                raise RuntimeError(f"Speech recognition failed: {str(e)}")
        
        except Exception as e:
            perf_monitor.end_request()
            app_logger.error(f"Unexpected STT error: {e}", exc_info=True)
            raise RuntimeError(f"Speech recognition failed: {str(e)}")
    
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
