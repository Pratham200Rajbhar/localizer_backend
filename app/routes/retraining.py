"""
Model retraining and evaluation routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job, JobType, JobStatus
from app.models.evaluation import Evaluation
from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    RetrainingRequest,
    RetrainingResponse
)
from app.schemas.job import JobResponse
from app.tasks.evaluation import evaluate_translation_task
from app.tasks.retraining import retrain_model_task
from app.utils.logger import app_logger

router = APIRouter(tags=["Evaluation & Retraining"])


@router.post("/evaluate/run", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def evaluate_translation(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate translation quality using BLEU, COMET, and other metrics
    
    Requires reference (ground truth) text
    """
    # Check job exists
    job_to_eval = db.query(Job).filter(Job.id == request.job_id).first()
    if not job_to_eval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    try:
        # Get hypothesis text from job if not provided
        hypothesis_text = request.hypothesis_text
        if not hypothesis_text:
            # In production, fetch from translation results
            hypothesis_text = "Translated text from job results"
        
        # Create evaluation job
        eval_job = Job(
            type=JobType.EVALUATION,
            status=JobStatus.QUEUED
        )
        db.add(eval_job)
        db.commit()
        db.refresh(eval_job)
        
        # Queue evaluation task
        task = evaluate_translation_task.delay(
            job_id=eval_job.id,
            reference_text=request.reference_text,
            hypothesis_text=hypothesis_text,
            language_pair=request.language_pair
        )
        
        eval_job.celery_task_id = task.id
        db.commit()
        
        app_logger.info(f"Evaluation job queued: job_id={eval_job.id}")
        
        return eval_job
    
    except Exception as e:
        app_logger.error(f"Evaluation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting evaluation"
        )


@router.get("/evaluate/results", response_model=List[EvaluationResponse])
async def get_evaluation_results(
    skip: int = 0,
    limit: int = 100,
    language_pair: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get evaluation results
    """
    query = db.query(Evaluation)
    
    if language_pair:
        query = query.filter(Evaluation.language_pair == language_pair)
    
    evaluations = query.offset(skip).limit(limit).all()
    
    return evaluations


@router.post("/retrain/trigger", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_retraining(
    request: RetrainingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger model retraining based on feedback and evaluation data
    
    Admin only
    """
    # Only admins can trigger retraining
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger retraining"
        )
    
    try:
        # Create retraining job
        job = Job(
            type=JobType.RETRAINING,
            status=JobStatus.QUEUED
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Queue retraining task
        task = retrain_model_task.delay(
            job_id=job.id,
            model_name=request.model_name,
            domain=request.domain,
            epochs=request.epochs,
            min_bleu_threshold=request.min_bleu_threshold
        )
        
        job.celery_task_id = task.id
        db.commit()
        
        app_logger.info(
            f"Retraining job queued: job_id={job.id}, model={request.model_name}"
        )
        
        return job
    
    except Exception as e:
        app_logger.error(f"Retraining error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting retraining"
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check status of any job (translation, STT, TTS, evaluation, retraining)
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job

