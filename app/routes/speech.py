"""
Speech (STT/TTS) routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_current_user
from app.core.config import SUPPORTED_LANGUAGES
from app.models.user import User
from app.models.job import Job, JobType, JobStatus
from app.schemas.speech import STTRequest, TTSRequest
from app.schemas.job import JobResponse
from app.tasks.speech import speech_to_text_task, text_to_speech_task
from app.utils.file_manager import file_manager
from app.utils.logger import app_logger

router = APIRouter(prefix="/speech", tags=["Speech"])

ALLOWED_AUDIO_FORMATS = {".wav", ".mp3", ".mp4", ".m4a", ".ogg", ".flac"}
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB


@router.post("/stt", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert speech to text (Speech-to-Text)
    
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
    
    await file.seek(0)
    
    try:
        # Save audio file
        saved_file = await file_manager.save_upload(file)
        
        # Create job
        job = Job(
            type=JobType.STT,
            status=JobStatus.QUEUED
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Queue Celery task
        task = speech_to_text_task.delay(
            job_id=job.id,
            audio_path=saved_file["file_path"],
            language=language
        )
        
        job.celery_task_id = task.id
        db.commit()
        
        app_logger.info(f"STT job queued: job_id={job.id}")
        
        return job
    
    except Exception as e:
        app_logger.error(f"STT error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing speech-to-text request"
        )


@router.post("/tts", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def text_to_speech(
    request: TTSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech (Text-to-Speech)
    
    Supports all 22 Indian languages
    """
    # Validate language
    if request.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{request.language}' not supported. Choose from 22 Indian languages"
        )
    
    try:
        # Create job
        job = Job(
            type=JobType.TTS,
            status=JobStatus.QUEUED
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Queue Celery task
        task = text_to_speech_task.delay(
            job_id=job.id,
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed
        )
        
        job.celery_task_id = task.id
        db.commit()
        
        app_logger.info(f"TTS job queued: job_id={job.id}, language={request.language}")
        
        return job
    
    except Exception as e:
        app_logger.error(f"TTS error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing text-to-speech request"
        )

