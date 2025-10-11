"""
Speech Engine for STT and TTS
"""
import time
import tempfile
from typing import Dict, Optional
from pathlib import Path
from app.core.config import get_settings, SUPPORTED_LANGUAGES
from app.utils.logger import app_logger
from app.utils.metrics import metrics

# Optional imports for speech libraries
try:
    import torch
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    app_logger.warning("Whisper not available - STT functionality disabled")

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except Exception as e:
    TTS_AVAILABLE = False
    app_logger.warning(f"TTS not available - TTS functionality disabled: {e}")

settings = get_settings()


class SpeechEngine:
    """Speech-to-Text and Text-to-Speech engine"""
    
    def __init__(self):
        try:
            import torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        except:
            self.device = "cpu"
        self.whisper_model = None
        self.tts_model = None
        app_logger.info(f"Speech Engine initialized (Whisper: {WHISPER_AVAILABLE}, TTS: {TTS_AVAILABLE})")
    
    def load_whisper(self, model_size: str = "base"):
        """
        Load Whisper model for STT
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        if not WHISPER_AVAILABLE:
            raise RuntimeError("Whisper is not installed. Install with: pip install openai-whisper")
        
        if self.whisper_model is not None:
            app_logger.info("Whisper model already loaded")
            return
        
        start_time = time.time()
        app_logger.info(f"Loading Whisper model: {model_size}")
        
        try:
            import whisper
            self.whisper_model = whisper.load_model(model_size, device=self.device)
            
            load_time = time.time() - start_time
            metrics.record_model_load_time(f"whisper-{model_size}", load_time)
            
            app_logger.info(f"Whisper model loaded in {load_time:.2f}s")
        
        except Exception as e:
            app_logger.error(f"Error loading Whisper: {e}")
            raise
    
    def load_tts(self):
        """Load TTS model"""
        if not TTS_AVAILABLE:
            raise RuntimeError("TTS is not installed. Install with: pip install TTS")
        
        if self.tts_model is not None:
            app_logger.info("TTS model already loaded")
            return
        
        start_time = time.time()
        app_logger.info("Loading TTS model")
        
        try:
            from TTS.api import TTS as TTSModel
            # Use a multilingual TTS model
            # For production, you'd want to use specific Indic language models
            self.tts_model = TTSModel(
                model_name="tts_models/multilingual/multi-dataset/your_tts",
                progress_bar=False,
                gpu=(self.device == "cuda")
            )
            
            load_time = time.time() - start_time
            metrics.record_model_load_time("tts-multilingual", load_time)
            
            app_logger.info(f"TTS model loaded in {load_time:.2f}s")
        
        except Exception as e:
            app_logger.error(f"Error loading TTS: {e}")
            # Fallback: use a simpler model
            try:
                from TTS.api import TTS as TTSModel
                self.tts_model = TTSModel(
                    model_name="tts_models/en/ljspeech/tacotron2-DDC",
                    progress_bar=False,
                    gpu=(self.device == "cuda")
                )
                app_logger.info("Loaded fallback TTS model")
            except Exception as e2:
                app_logger.error(f"Error loading fallback TTS: {e2}")
                raise
    
    def speech_to_text(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Convert speech to text using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Optional language hint
        
        Returns:
            Dict with transcript and metadata
        """
        start_time = time.time()
        
        try:
            # Load Whisper if not loaded
            if self.whisper_model is None:
                self.load_whisper("base")
            
            # Transcribe
            app_logger.info(f"Transcribing audio: {audio_path}")
            
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                fp16=(self.device == "cuda")
            )
            
            duration = time.time() - start_time
            detected_lang = result.get("language", language or "unknown")
            
            if detected_lang in SUPPORTED_LANGUAGES or detected_lang == "en":
                metrics.record_stt(detected_lang)
            
            app_logger.info(
                f"Transcription completed in {duration:.2f}s, "
                f"detected language: {detected_lang}"
            )
            
            return {
                "transcript": result["text"],
                "language_detected": detected_lang,
                "confidence": 0.9,
                "duration": duration,
                "segments": result.get("segments", [])
            }
        
        except Exception as e:
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
        Convert text to speech
        
        Args:
            text: Text to convert
            language: Language code
            output_path: Path to save audio file
            voice: Voice type
            speed: Speech speed multiplier
        
        Returns:
            Dict with audio path and metadata
        """
        start_time = time.time()
        
        try:
            # Load TTS if not loaded
            if self.tts_model is None:
                self.load_tts()
            
            app_logger.info(f"Generating TTS for language: {language}")
            
            # Map language to TTS speaker if available
            # For demo, we'll use English speaker for all languages
            # In production, you'd have language-specific models
            
            # Generate speech
            self.tts_model.tts_to_file(
                text=text,
                file_path=output_path,
                speaker=None,
                language="en",  # Would map to actual language
                speed=speed
            )
            
            duration = time.time() - start_time
            metrics.record_tts(language)
            
            # Get audio duration (approximate)
            import wave
            try:
                with wave.open(output_path, 'rb') as audio_file:
                    frames = audio_file.getnframes()
                    rate = audio_file.getframerate()
                    audio_duration = frames / float(rate)
            except:
                audio_duration = len(text) * 0.1  # Rough estimate
            
            app_logger.info(f"TTS generation completed in {duration:.2f}s")
            
            return {
                "audio_path": output_path,
                "language": language,
                "duration": audio_duration,
                "generation_time": duration,
                "format": "wav"
            }
        
        except Exception as e:
            app_logger.error(f"TTS error: {e}")
            raise


# Global speech engine instance
speech_engine = SpeechEngine()

