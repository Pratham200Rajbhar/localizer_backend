"""
Translation Celery tasks
"""
from datetime import datetime
from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.job import Job, JobStatus
from app.models.translation import Translation
from app.services.nlp_engine import nlp_engine
from app.services.localization import localization_engine
from app.utils.file_manager import file_manager
from app.utils.logger import app_logger


@celery_app.task(bind=True, name="app.tasks.translation.translate_text")
def translate_text_task(
    self,
    job_id: int,
    text: str,
    source_lang: str,
    target_lang: str,
    domain: str = None,
    apply_localization: bool = True
):
    """
    Celery task for text translation
    
    Args:
        job_id: Job ID
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        domain: Optional domain
        apply_localization: Whether to apply localization
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
        
        app_logger.info(f"Translation task started: job_id={job_id}")
        
        # Perform translation
        result = nlp_engine.translate(text, source_lang, target_lang, domain)
        job.progress = 60.0
        db.commit()
        
        translated_text = result["translated_text"]
        
        # Apply localization if requested
        if apply_localization:
            loc_result = localization_engine.localize(
                translated_text,
                target_lang,
                domain
            )
            translated_text = loc_result["localized_text"]
        
        job.progress = 80.0
        db.commit()
        
        # Save translation to file
        translation_data = {
            "source_text": text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "model_used": result["model_used"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        output_path = file_manager.save_translation(
            job_id,
            target_lang,
            translation_data
        )
        
        # Save to database
        translation = Translation(
            job_id=job_id,
            source_language=source_lang,
            target_language=target_lang,
            source_text=text,
            translated_text=translated_text,
            output_path=output_path,
            model_used=result["model_used"],
            confidence_score=int(result.get("confidence_score", 0.85) * 100)
        )
        db.add(translation)
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        job.result_path = output_path
        db.commit()
        
        app_logger.info(f"Translation task completed: job_id={job_id}")
        
        return {
            "status": "completed",
            "translation_id": translation.id,
            "output_path": output_path
        }
    
    except Exception as e:
        app_logger.error(f"Translation task failed: {e}")
        
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        db.close()

