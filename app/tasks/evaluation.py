"""
Evaluation Celery tasks
"""
from datetime import datetime
from typing import Dict
from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.job import Job, JobStatus
from app.models.evaluation import Evaluation
from app.utils.logger import app_logger
import sacrebleu


@celery_app.task(bind=True, name="app.tasks.evaluation.evaluate_translation")
def evaluate_translation_task(
    self,
    job_id: int,
    reference_text: str,
    hypothesis_text: str,
    language_pair: str,
    model_name: str = None
) -> Dict:
    """
    Celery task for evaluating translation quality
    
    Args:
        job_id: Job ID
        reference_text: Reference/ground truth text
        hypothesis_text: Hypothesis/translated text
        language_pair: Language pair (e.g., "en-hi")
        model_name: Model name
    
    Returns:
        Evaluation metrics
    """
    db = SessionLocal()
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.progress = 10.0
        db.commit()
        
        app_logger.info(f"Evaluation task started: job_id={job_id}")
        
        # Compute BLEU score
        bleu = sacrebleu.sentence_bleu(hypothesis_text, [reference_text])
        bleu_score = bleu.score / 100.0
        
        job.progress = 50.0
        db.commit()
        
        # In production, you'd also compute COMET, TER, METEOR scores
        # For now, we'll use placeholder values
        comet_score = 0.75
        ter_score = 0.35
        meteor_score = 0.65
        
        job.progress = 80.0
        db.commit()
        
        # Save evaluation
        evaluation = Evaluation(
            job_id=job_id,
            model_name=model_name,
            language_pair=language_pair,
            bleu_score=bleu_score,
            comet_score=comet_score,
            ter_score=ter_score,
            meteor_score=meteor_score,
            reference_text=reference_text,
            hypothesis_text=hypothesis_text
        )
        db.add(evaluation)
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        db.commit()
        
        app_logger.info(
            f"Evaluation completed: job_id={job_id}, "
            f"BLEU={bleu_score:.4f}, COMET={comet_score:.4f}"
        )
        
        return {
            "status": "completed",
            "evaluation_id": evaluation.id,
            "bleu_score": bleu_score,
            "comet_score": comet_score,
            "ter_score": ter_score,
            "meteor_score": meteor_score
        }
    
    except Exception as e:
        app_logger.error(f"Evaluation task failed: {e}")
        
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        db.close()

