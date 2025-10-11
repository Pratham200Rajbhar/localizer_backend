"""
Speech (STT/TTS) Celery tasks
"""
from datetime import datetime
from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.job import Job, JobStatus
from app.services.speech_engine import speech_engine
from app.utils.file_manager import file_manager
from app.utils.logger import app_logger


@celery_app.task(bind=True, name="app.tasks.speech.speech_to_text")
def speech_to_text_task(self, job_id: int, audio_path: str, language: str = None):
    """
    Celery task for speech-to-text conversion
    
    Args:
        job_id: Job ID
        audio_path: Path to audio file
        language: Optional language hint
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
        
        app_logger.info(f"STT task started: job_id={job_id}")
        
        # Perform transcription
        result = speech_engine.speech_to_text(audio_path, language)
        job.progress = 80.0
        db.commit()
        
        # Save transcript
        transcript_path = file_manager.save_transcript(job_id, result["transcript"])
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        job.result_path = transcript_path
        db.commit()
        
        app_logger.info(f"STT task completed: job_id={job_id}")
        
        return {
            "status": "completed",
            "transcript": result["transcript"],
            "language_detected": result["language_detected"],
            "output_path": transcript_path
        }
    
    except Exception as e:
        app_logger.error(f"STT task failed: {e}")
        
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        db.close()


@celery_app.task(bind=True, name="app.tasks.speech.text_to_speech")
def text_to_speech_task(
    self,
    job_id: int,
    text: str,
    language: str,
    voice: str = "default",
    speed: float = 1.0
):
    """
    Celery task for text-to-speech conversion
    
    Args:
        job_id: Job ID
        text: Text to convert
        language: Language code
        voice: Voice type
        speed: Speech speed
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
        
        app_logger.info(f"TTS task started: job_id={job_id}")
        
        # Generate audio path
        output_dir = file_manager.create_output_dir(job_id)
        audio_path = str(output_dir / f"tts_{language}.wav")
        
        # Perform TTS
        result = speech_engine.text_to_speech(text, language, audio_path, voice, speed)
        job.progress = 80.0
        db.commit()
        
        # Update job
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        job.result_path = audio_path
        db.commit()
        
        app_logger.info(f"TTS task completed: job_id={job_id}")
        
        return {
            "status": "completed",
            "audio_path": audio_path,
            "language": language,
            "duration": result["duration"]
        }
    
    except Exception as e:
        app_logger.error(f"TTS task failed: {e}")
        
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        db.close()

