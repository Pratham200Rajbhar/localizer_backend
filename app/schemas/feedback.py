"""
Feedback schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""
    job_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comments: Optional[str] = Field(None, max_length=2000)
    corrections: Optional[dict] = Field(None, description="JSON with text corrections")


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: int
    job_id: int
    user_id: int
    rating: int
    comments: Optional[str]
    corrections: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    """Schema for feedback statistics"""
    total_feedback: int
    average_rating: float
    rating_distribution: dict
    top_issues: list

