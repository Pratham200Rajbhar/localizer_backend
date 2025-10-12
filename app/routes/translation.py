"""
Translation routes
"""
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.core.security import get_current_user
from app.core.config import SUPPORTED_LANGUAGES
from app.models.user import User
from app.models.file import File as FileModel
from app.schemas.translation import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationResponse,
    LanguageDetectionResponse
)
from app.services import nlp_engine
from app.utils.logger import app_logger

router = APIRouter(tags=["Translation"])


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages (22 Indian languages)
    """
    return SUPPORTED_LANGUAGES


@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Auto-detect language of input text
    Expected JSON: {"text": "text to analyze"}
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required"
            )
        
        result = nlp_engine.detect_language(text)
        app_logger.info(f"Language detected: {result['detected_language']}")
        return result
    except Exception as e:
        app_logger.error(f"Language detection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error detecting language"
        )


@router.post("/translate", response_model=BatchTranslationResponse)
async def translate(
    request: TranslationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Translate text to target languages (direct synchronous processing)
    
    Returns translation results immediately
    """
    # Validate that we have either text or file_id
    if not request.text and not request.file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'text' or 'file_id' must be provided"
        )
    
    # Validate source language is supported
    if request.source_language not in SUPPORTED_LANGUAGES and request.source_language != "en":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source language '{request.source_language}' not supported. Choose from 22 Indian languages or English."
        )
    
    # Validate all target languages are supported
    for target_lang in request.target_languages:
        if target_lang not in SUPPORTED_LANGUAGES and target_lang != "en":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language '{target_lang}' not supported. Choose from 22 Indian languages or English."
            )
    
    # If file_id provided, check it exists and extract text
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
        
        # Extract actual text from file
        try:
            from app.utils.text_extractor import text_extractor
            
            extraction_result = text_extractor.extract_text(file.path)
            text_to_translate = extraction_result["text"]
            
            if not text_to_translate or len(text_to_translate.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No text content found in file"
                )
            
            app_logger.info(f"Extracted {extraction_result.get('word_count', 0)} words from {file.filename}")
            
        except Exception as e:
            app_logger.error(f"Text extraction failed for file {file.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract text from file: {str(e)}"
            )
    else:
        text_to_translate = request.text
    
    if not text_to_translate or len(text_to_translate.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to translate cannot be empty"
        )
    
    try:
        # Perform translations directly
        results = []
        total_start_time = time.time()
        
        for target_lang in request.target_languages:
            app_logger.info(
                f"Starting translation: {request.source_language} -> {target_lang}"
            )
            
            # Direct translation using NLP engine
            translation_result = nlp_engine.translate(
                text=text_to_translate,
                source_lang=request.source_language,
                target_lang=target_lang,
                domain=request.domain
            )
            
            # Apply localization if requested
            if request.apply_localization and request.domain:
                try:
                    from app.services.localization import localization_engine
                    localized_result = localization_engine.localize(
                        translation_result["translated_text"],
                        target_lang,
                        request.domain
                    )
                    translation_result["translated_text"] = localized_result["localized_text"]
                    app_logger.info(f"Applied localization for domain: {request.domain}")
                except Exception as e:
                    app_logger.warning(f"Localization failed: {e}, using base translation")
            
            # Save translation to database for evaluation/feedback
            translation_id = None
            try:
                app_logger.info(f"Attempting to save translation to database for user: {current_user.id}")
                from app.models.translation import Translation
                translation_record = Translation(
                    user_id=current_user.id,
                    source_language=translation_result["source_language"],
                    target_language=translation_result["target_language"],
                    source_text=text_to_translate,
                    translated_text=translation_result["translated_text"],
                    model_used=translation_result["model_used"],
                    confidence_score=translation_result["confidence_score"],
                    domain=request.domain,
                    duration=translation_result["duration"]
                )
                app_logger.info("Translation record created, attempting to save...")
                db.add(translation_record)
                db.commit()
                db.refresh(translation_record)
                translation_id = translation_record.id
                app_logger.info(f"Translation saved to database with ID: {translation_record.id}")
            except Exception as db_error:
                app_logger.error(f"Failed to save translation to database: {db_error}")
                import traceback
                app_logger.error(f"Database error traceback: {traceback.format_exc()}")
                # Don't fail the request if database save fails
                db.rollback()

            # Create response
            response = TranslationResponse(
                translated_text=translation_result["translated_text"],
                source_language=translation_result["source_language"],
                target_language=translation_result["target_language"],
                source_language_name=translation_result["source_language_name"],
                target_language_name=translation_result["target_language_name"],
                model_used=translation_result["model_used"],
                confidence_score=translation_result["confidence_score"],
                duration=translation_result["duration"],
                domain=request.domain,
                translation_id=translation_id
            )
            
            results.append(response)
            
            app_logger.info(
                f"Translation completed: {request.source_language} -> {target_lang} "
                f"in {translation_result['duration']:.2f}s"
            )
        
        total_duration = time.time() - total_start_time
        
        return BatchTranslationResponse(
            results=results,
            total_translations=len(results),
            total_duration=total_duration
        )
    
    except ValueError as e:
        app_logger.error(f"Translation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        app_logger.error(f"Translation error: {e}")
        
        # Check if this is a transformers import error, use fallback
        if "transformers" in str(e) or "huggingface_hub" in str(e):
            app_logger.warning("Transformers error detected, using fallback translation")
            results = []
            total_start_time = time.time()
            
            for target_lang in request.target_languages:
                # Create fallback translation response
                fallback_text = f"[MOCK TRANSLATION: {request.source_language} to {target_lang}] {text_to_translate[:100]}..."
                
                response = TranslationResponse(
                    translated_text=fallback_text,
                    source_language=request.source_language,
                    target_language=target_lang,
                    source_language_name="English" if request.source_language == "en" else request.source_language.title(),
                    target_language_name=target_lang.title(),
                    model_used="Fallback",
                    confidence_score=0.5,
                    duration=0.1,
                    domain=request.domain,
                    translation_id=None
                )
                results.append(response)
            
            total_duration = time.time() - total_start_time
            
            return BatchTranslationResponse(
                results=results,
                total_translations=len(results),
                total_duration=total_duration
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Translation failed"
            )


@router.post("/localize/context")
async def apply_localization(
    text: str,
    language: str,
    domain: str,
    current_user: User = Depends(get_current_user)
):
    """
    Apply domain-specific and cultural localization to text
    """
    # Validate language
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language {language} not supported"
        )
    
    if not text or len(text.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    try:
        from app.services.localization import localization_engine
        
        # Apply localization directly
        result = localization_engine.localize(
            text=text,
            language=language,
            domain=domain
        )
        
        app_logger.info(f"Localization applied for {language} in {domain} domain")
        
        return {
            "original_text": text,
            "localized_text": result["localized_text"],
            "language": language,
            "domain": domain,
            "changes_applied": result.get("changes_applied", [])
        }
    
    except Exception as e:
        app_logger.error(f"Localization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Localization failed: {str(e)}"
        )

