"""
Retraining Celery tasks
"""
from datetime import datetime
from typing import Dict
from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.job import Job, JobStatus
from app.services.retrain_manager import retrain_manager
from app.utils.logger import app_logger


@celery_app.task(bind=True, name="app.tasks.retraining.retrain_model")
def retrain_model_task(
    self,
    job_id: int,
    model_name: str,
    domain: str = None,
    epochs: int = 3,
    min_bleu_threshold: float = None
) -> Dict:
    """
    Celery task for model retraining
    
    Args:
        job_id: Job ID
        model_name: Model to retrain
        domain: Optional domain
        epochs: Number of epochs
        min_bleu_threshold: Minimum BLEU threshold
    
    Returns:
        Retraining results
    """
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.progress = 5.0
        db.commit()
        
        app_logger.info(f"Retraining task started: job_id={job_id}, model={model_name}")
        
        # Simulate retraining process
        # In production, this would:
        # 1. Load training data
        # 2. Prepare dataset
        # 3. Fine-tune model
        # 4. Validate performance
        # 5. Deploy if improved
        
        for progress in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
            job.progress = float(progress)
            db.commit()
            app_logger.info(f"Retraining progress: {progress}%")
        
        # Trigger actual retraining
        result = retrain_manager.trigger_retraining(
            model_name,
            domain,
            epochs,
            min_bleu_threshold
        )
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        db.commit()
        
        app_logger.info(f"Retraining completed: job_id={job_id}")
        
        return {
            "status": "completed",
            "model_name": model_name,
            "domain": domain,
            "epochs": epochs,
            "message": "Retraining completed successfully"
        }
    
    except Exception as e:
        app_logger.error(f"Retraining task failed: {e}")
        
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        db.close()

