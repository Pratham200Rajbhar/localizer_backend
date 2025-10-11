"""
Job schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enum"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Job type enum"""
    TRANSLATION = "translation"
    STT = "stt"
    TTS = "tts"
    LOCALIZATION = "localization"
    EVALUATION = "evaluation"
    RETRAINING = "retraining"


class JobResponse(BaseModel):
    """Schema for job response"""
    id: int
    celery_task_id: Optional[str]
    file_id: Optional[int]
    type: str
    status: str
    progress: float
    result_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    """Schema for job status check"""
    job_id: int
    status: str
    progress: float
    result: Optional[dict] = None
    error: Optional[str] = None

