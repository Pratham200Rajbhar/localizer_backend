"""
Job Status and Background Task Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.direct_retrain import DirectRetrainManager
from app.utils.logger import app_logger

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{task_id}")
async def get_job_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a background job/task
    
    Args:
        task_id: Celery task ID
    
    Returns:
        Task status and results
    """
    try:
        task_status = get_task_status(task_id)
        
        return {
            "task_id": task_id,
            "status": task_status["status"],
            "result": task_status.get("result"),
            "error": task_status.get("traceback")
        }
    
    except Exception as e:
        app_logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status"
        )


@router.delete("/{task_id}")
async def cancel_job(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running background job
    
    Args:
        task_id: Celery task ID
    
    Returns:
        Cancellation status
    """
    try:
        cancelled = cancel_task(task_id)
        
        app_logger.info(f"Task {task_id} cancelled by user {current_user.id}")
        
        return {
            "task_id": task_id,
            "cancelled": cancelled,
            "message": "Task cancellation requested"
        }
    
    except Exception as e:
        app_logger.error(f"Error cancelling task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel task"
        )


@router.post("/translate/async")
async def start_translation_job(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Start asynchronous translation job
    Expected JSON: {
        "text": "text to translate",
        "source_language": "en", 
        "target_languages": ["hi", "bn"],
        "domain": "healthcare"
    }
    """
    try:
        text = request.get("text")
        source_lang = request.get("source_language")
        target_languages = request.get("target_languages", [])
        domain = request.get("domain")
        
        if not text or not source_lang or not target_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="text, source_language, and target_languages are required"
            )
        
        # Start batch translation task
        task = batch_translate_task.delay(
            text=text,
            source_lang=source_lang,
            target_languages=target_languages,
            domain=domain,
            user_id=current_user.id
        )
        
        app_logger.info(f"Started translation job {task.id} for user {current_user.id}")
        
        return {
            "task_id": task.id,
            "status": "STARTED",
            "message": "Translation job started",
            "check_status_url": f"/jobs/{task.id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error starting translation job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start translation job"
        )


@router.post("/evaluate/async")
async def start_evaluation_job(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Start asynchronous evaluation job
    Expected JSON: {
        "translation_id": 123,
        "reference_text": "reference translation"
    }
    """
    try:
        translation_id = request.get("translation_id")
        reference_text = request.get("reference_text")
        
        if not translation_id or not reference_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="translation_id and reference_text are required"
            )
        
        # Start evaluation task
        task = evaluate_translation_task.delay(
            translation_id=translation_id,
            reference_text=reference_text,
            evaluator_id=current_user.id
        )
        
        app_logger.info(f"Started evaluation job {task.id} for translation {translation_id}")
        
        return {
            "task_id": task.id,
            "status": "STARTED", 
            "message": "Evaluation job started",
            "check_status_url": f"/jobs/{task.id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error starting evaluation job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start evaluation job"
        )


@router.post("/retrain/trigger")
async def trigger_retrain_job(
    request: dict = None,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger model retraining (direct implementation, no Celery)
    As specified in the master prompt requirements
    Expected JSON: {
        "domain": "healthcare", 
        "epochs": 3,
        "languages": ["hi", "bn", "te"]
    }
    """
    from app.services.direct_retrain import direct_retrain_manager
    
    # Only admins can trigger retraining
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can trigger model retraining"
        )
    
    try:
        domain = "general"
        epochs = 3
        languages = None
        
        if request:
            domain = request.get("domain", "general")
            epochs = request.get("epochs", 3)
            languages = request.get("languages")
        
        # Default to all supported languages if none specified
        if languages is None:
            languages = list(SUPPORTED_LANGUAGES.keys())
        
        # Start retraining directly (no Celery as per prompt)
        result = direct_retrain_manager.trigger_retraining(
            domain=domain,
            epochs=epochs,
            languages=languages
        )
        
        app_logger.info(f"Completed retraining job {result['retrain_id']} for domain {domain}")
        
        return {
            "retrain_id": result["retrain_id"],
            "status": result["status"],
            "message": "Model retraining completed successfully" if result["status"] == "completed" else "Model retraining failed",
            "domain": domain,
            "epochs": epochs,
            "languages": languages,
            "results": result.get("results", {}),
            "validation": result.get("validation", {}),
            "error": result.get("error")
        }
    
    except Exception as e:
        app_logger.error(f"Error during retraining: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete retraining: {str(e)}"
        )