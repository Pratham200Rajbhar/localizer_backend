"""
Job Management Routes (Direct execution, no Celery)
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import asyncio

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.direct_retrain import DirectRetrainManager
from app.utils.logger import app_logger

router = APIRouter(prefix="/jobs", tags=["Job Management"])

# In-memory job tracking (for production, consider Redis)
active_jobs = {}


@router.post("/retrain")
async def trigger_model_retraining(
    background_tasks: BackgroundTasks,
    domain: str = "general",
    model_type: str = "indicTrans2",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger model retraining (direct implementation, no Celery)
    
    Args:
        domain: Domain to retrain for (healthcare, construction, general)
        model_type: Type of model to retrain (indicTrans2, llama3)
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Learning rate for training
        
    Returns:
        Job ID and status
    """
    # Check permissions
    if current_user.role not in ["admin", "reviewer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and reviewers can trigger retraining"
        )
    
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "started",
            "started_at": datetime.utcnow().isoformat(),
            "domain": domain,
            "model_type": model_type,
            "epochs": epochs,
            "user_id": current_user.id,
            "progress": 0,
            "message": "Initializing retraining..."
        }
        
        # Start retraining directly (no Celery as per prompt)
        retrain_manager = DirectRetrainManager()
        
        # Add background task
        background_tasks.add_task(
            run_retraining_job,
            job_id,
            retrain_manager,
            domain,
            model_type,
            epochs,
            batch_size,
            learning_rate,
            current_user.id,
            db
        )
        
        app_logger.info(f"Retraining job {job_id} started by user {current_user.id}")
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Model retraining started",
            "domain": domain,
            "model_type": model_type,
            "estimated_duration": f"{epochs * 10} minutes"
        }
        
    except Exception as e:
        app_logger.error(f"Failed to start retraining job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start retraining: {str(e)}"
        )


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a running job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status and progress
    """
    if job_id not in active_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_info = active_jobs[job_id]
    
    # Check if user can view this job
    if current_user.role != "admin" and job_info.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this job"
        )
    
    return {
        "job_id": job_id,
        **job_info
    }


@router.get("")
async def list_active_jobs(
    current_user: User = Depends(get_current_user)
):
    """
    List all active jobs (admin) or user's jobs
    
    Returns:
        List of jobs
    """
    if current_user.role == "admin":
        # Admins can see all jobs
        jobs = [{"job_id": job_id, **info} for job_id, info in active_jobs.items()]
    else:
        # Users can only see their own jobs
        jobs = [
            {"job_id": job_id, **info} 
            for job_id, info in active_jobs.items() 
            if info.get("user_id") == current_user.id
        ]
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }


@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Cancellation status
    """
    if job_id not in active_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_info = active_jobs[job_id]
    
    # Check permissions
    if current_user.role != "admin" and job_info.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to cancel this job"
        )
    
    # Mark as cancelled
    active_jobs[job_id]["status"] = "cancelled"
    active_jobs[job_id]["message"] = "Job cancelled by user"
    active_jobs[job_id]["cancelled_at"] = datetime.utcnow().isoformat()
    
    app_logger.info(f"Job {job_id} cancelled by user {current_user.id}")
    
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancellation requested"
    }


async def run_retraining_job(
    job_id: str,
    retrain_manager: DirectRetrainManager,
    domain: str,
    model_type: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    user_id: int,
    db: Session
):
    """
    Background task to run model retraining
    """
    try:
        # Update job status
        active_jobs[job_id]["status"] = "running"
        active_jobs[job_id]["message"] = "Preparing training data..."
        active_jobs[job_id]["progress"] = 10
        
        # Simulate progress updates (replace with actual training progress)
        for progress in [25, 50, 75]:
            if active_jobs[job_id]["status"] == "cancelled":
                app_logger.info(f"Job {job_id} was cancelled")
                return
            
            active_jobs[job_id]["progress"] = progress
            active_jobs[job_id]["message"] = f"Training in progress... {progress}%"
            await asyncio.sleep(2)  # Simulate work
        
        # Run actual retraining
        result = await retrain_manager.retrain_model(
            domain=domain,
            model_type=model_type,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate
        )
        
        # Update completion status
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["message"] = "Retraining completed successfully"
        active_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        active_jobs[job_id]["result"] = result
        
        app_logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        # Update error status
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["message"] = f"Retraining failed: {str(e)}"
        active_jobs[job_id]["error"] = str(e)
        active_jobs[job_id]["failed_at"] = datetime.utcnow().isoformat()
        
        app_logger.error(f"Job {job_id} failed: {e}")


@router.post("/cleanup")
async def cleanup_completed_jobs(
    current_user: User = Depends(get_current_user)
):
    """
    Clean up completed/failed jobs (admin only)
    
    Returns:
        Cleanup summary
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can cleanup jobs"
        )
    
    completed_statuses = ["completed", "failed", "cancelled"]
    jobs_to_remove = [
        job_id for job_id, info in active_jobs.items()
        if info.get("status") in completed_statuses
    ]
    
    for job_id in jobs_to_remove:
        del active_jobs[job_id]
    
    app_logger.info(f"Cleaned up {len(jobs_to_remove)} completed jobs")
    
    return {
        "cleaned_jobs": len(jobs_to_remove),
        "remaining_jobs": len(active_jobs)
    }