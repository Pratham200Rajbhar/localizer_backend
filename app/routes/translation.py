"""
Translation routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.core.security import get_current_user
from app.core.config import SUPPORTED_LANGUAGES
from app.models.user import User
from app.models.job import Job, JobType, JobStatus
from app.models.file import File as FileModel
from app.schemas.translation import (
    TranslationRequest,
    TranslationResponse,
    LanguageDetectionResponse
)
from app.schemas.job import JobResponse
from app.services.nlp_engine import nlp_engine
from app.tasks.translation import translate_text_task
from app.utils.logger import app_logger
from datetime import datetime

router = APIRouter(tags=["Translation"])


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages (22 Indian languages)
    """
    return {"languages": SUPPORTED_LANGUAGES}


@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Auto-detect language of input text
    """
    try:
        result = nlp_engine.detect_language(text)
        app_logger.info(f"Language detected: {result['detected_language']}")
        return result
    except Exception as e:
        app_logger.error(f"Language detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error detecting language"
        )


@router.post("/translate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def translate(
    request: TranslationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Translate text or file to target languages
    
    Returns a job ID that can be used to check status and get results
    """
    # Validate that we have either text or file_id
    if not request.text and not request.file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'text' or 'file_id' must be provided"
        )
    
    # If file_id provided, check it exists
    if request.file_id:
        file = db.query(FileModel).filter(FileModel.id == request.file_id).first()
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check permissions
        if current_user.role != "admin" and file.uploader_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # For now, we'll use dummy text (in production, extract from file)
        text_to_translate = f"Content from file: {file.filename}"
    else:
        text_to_translate = request.text
    
    try:
        # Create a job for each target language
        jobs = []
        
        for target_lang in request.target_languages:
            # Create job entry
            job = Job(
                type=JobType.TRANSLATION,
                status=JobStatus.QUEUED,
                file_id=request.file_id
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
            # Queue Celery task
            task = translate_text_task.delay(
                job_id=job.id,
                text=text_to_translate,
                source_lang=request.source_language,
                target_lang=target_lang,
                domain=request.domain,
                apply_localization=request.apply_localization
            )
            
            # Update job with Celery task ID
            job.celery_task_id = task.id
            db.commit()
            
            jobs.append(job)
            
            app_logger.info(
                f"Translation job queued: {request.source_language}->{target_lang}, "
                f"job_id={job.id}"
            )
        
        # Return the first job (or you could return all jobs)
        return jobs[0]
    
    except Exception as e:
        app_logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting translation job"
        )


@router.post("/localize/context", status_code=status.HTTP_202_ACCEPTED)
async def apply_localization(
    translation_id: int,
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply domain-specific and cultural localization to an existing translation
    """
    from app.models.translation import Translation
    from app.services.localization import localization_engine
    
    # Get translation
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    try:
        # Apply localization
        result = localization_engine.localize(
            translation.translated_text,
            translation.target_language,
            domain
        )
        
        # Update translation
        translation.translated_text = result["localized_text"]
        db.commit()
        
        app_logger.info(f"Localization applied to translation {translation_id}")
        
        return {
            "status": "success",
            "translation_id": translation_id,
            "localized_text": result["localized_text"]
        }
    
    except Exception as e:
        app_logger.error(f"Localization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error applying localization"
        )

