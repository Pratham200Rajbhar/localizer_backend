"""
Evaluation schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EvaluationRequest(BaseModel):
    """Schema for evaluation request"""
    job_id: int
    reference_text: str = Field(..., description="Ground truth/reference translation")
    hypothesis_text: Optional[str] = Field(None, description="If not provided, uses job output")
    language_pair: str = Field(..., description="e.g., 'en-hi'")


class EvaluationResponse(BaseModel):
    """Schema for evaluation response"""
    id: int
    job_id: int
    model_name: Optional[str]
    language_pair: Optional[str]
    bleu_score: Optional[float]
    comet_score: Optional[float]
    ter_score: Optional[float]
    meteor_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class RetrainingRequest(BaseModel):
    """Schema for retraining request"""
    model_name: str = Field(..., description="Model to retrain")
    domain: Optional[str] = Field(None, description="Domain to focus on")
    epochs: int = Field(3, ge=1, le=10)
    min_bleu_threshold: Optional[float] = Field(None, description="Minimum BLEU score to trigger retraining")


class RetrainingResponse(BaseModel):
    """Schema for retraining response"""
    job_id: int
    status: str
    message: str

