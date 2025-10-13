"""
Speech (STT/TTS) routes
"""
import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.config import SUPPORTED_LANGUAGES, get_settings
from app.schemas.speech import STTRequest, TTSRequest, STTResponse, TTSResponse
from app.services import speech_engine
from app.utils.file_manager import file_manager
from app.utils.logger import app_logger

settings = get_settings()

router = APIRouter(prefix="/speech", tags=["Speech"])

ALLOWED_AUDIO_FORMATS = {".wav", ".mp3", ".mp4", ".m4a", ".ogg", ".flac"}
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB


@router.post("/stt/test")
async def test_stt():
    """
    Test STT endpoint availability
    """
    return {
        "status": "available",
        "message": "Speech-to-Text service is operational",
        "supported_formats": list(ALLOWED_AUDIO_FORMATS),
        "max_file_size_mb": MAX_AUDIO_SIZE // (1024*1024)
    }


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    """
    Convert speech to text (Speech-to-Text) - Direct processing
    
    Supported formats: WAV, MP3, MP4, M4A, OGG, FLAC
    Maximum size: 100 MB
    """
    # Validate file extension
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Audio format not supported. Allowed: {', '.join(ALLOWED_AUDIO_FORMATS)}"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_AUDIO_SIZE // (1024*1024)} MB"
        )
    
    # Validate language if provided
    if language and language not in SUPPORTED_LANGUAGES and language != "en":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{language}' not supported"
        )
    
    try:
        # Save audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_audio_path = temp_file.name
        
        app_logger.info(f"Processing STT for file: {file.filename} ({len(content)} bytes)")
        
        # Validate audio file quality
        validation = speech_engine.validate_audio_file(temp_audio_path)
        if not validation.get("is_valid", True):
            if validation.get("is_silent", False):
                raise ValueError("Audio file appears to contain only silence or very low audio")
            if validation.get("sample_rate", 0) < 8000:
                raise ValueError("Audio sample rate too low (minimum 8kHz required)")
        
        # Perform STT directly
        result = await speech_engine.speech_to_text(
            audio_path=temp_audio_path,
            language=language
        )
        
        # Clean up temporary file
        os.unlink(temp_audio_path)
        
        app_logger.info(f"STT completed: {result['language']} detected")
        
        # Get language name from SUPPORTED_LANGUAGES or default
        language_name = SUPPORTED_LANGUAGES.get(result["language"], result["language"].title())
        
        return STTResponse(
            transcript=result["text"],
            language_detected=result["language"], 
            language_name=language_name,
            confidence=result["confidence"],
            duration=result["duration"],
            segments=result["segments"],
            model_used="whisper-large-v3"
        )
    
    except ValueError as e:
        # Clean up temp file if it exists
        try:
            os.unlink(temp_audio_path)
        except:
            pass
        app_logger.error(f"STT validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Clean up temp file if it exists
        try:
            os.unlink(temp_audio_path)
        except:
            pass
        app_logger.error(f"STT error: {e}")
        import traceback
        app_logger.error(f"STT traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech-to-text processing failed: {str(e)}"
        )


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest
):
    """
    Convert text to speech (Text-to-Speech) - Direct processing
    
    Supports all 22 Indian languages
    """
    # Validate input text
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    try:
        # Create unique output filename as MP3
        import uuid
        output_filename = f"tts_{request.language}_{uuid.uuid4().hex[:8]}.mp3"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        # Ensure output directory exists
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        app_logger.info(f"Processing TTS for language: {request.language}")
        
        # Perform TTS directly
        result = await speech_engine.text_to_speech(
            text=request.text,
            language=request.language,
            output_path=output_path
        )
        
        app_logger.info(f"TTS completed: {result['language']} audio generated")
        
        # Get language name
        language_name = SUPPORTED_LANGUAGES.get(result["language"], result["language"].title())
        
        return TTSResponse(
            audio_path=result["output_path"],
            language=result["language"],
            language_name=language_name,
            duration=result["generation_time"],
            generation_time=result["generation_time"],
            format="mp3"
        )
    
    except ValueError as e:
        app_logger.error(f"TTS validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        app_logger.error(f"TTS error: {e}")
        import traceback
        app_logger.error(f"TTS traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-speech processing failed: {str(e)}"
        )


@router.get("/tts/download/{filename}")
async def download_audio(
    filename: str
):
    """
    Download generated audio file
    """
    audio_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(audio_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    return FileResponse(
        path=audio_path,
        filename=filename,
        media_type="audio/wav"
    )

