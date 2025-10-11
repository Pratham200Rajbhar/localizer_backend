"""
Feedback routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.translation import Translation
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.utils.logger import app_logger
from app.utils.metrics import metrics

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a translation/job
    
    Rating: 1-5 stars
    """
    # Check translation exists
    translation = db.query(Translation).filter(Translation.id == feedback_data.translation_id).first()
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    try:
        # Create feedback
        feedback = Feedback(
            translation_id=feedback_data.translation_id,
            user_id=current_user.id,
            rating=feedback_data.rating,
            comments=feedback_data.comments,
            corrections=str(feedback_data.corrections) if feedback_data.corrections else None
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        # Record metrics
        metrics.record_feedback(feedback_data.rating)
        
        app_logger.info(
            f"Feedback submitted: translation_id={feedback_data.translation_id}, "
            f"rating={feedback_data.rating}, user={current_user.username}"
        )
        
        return feedback
    
    except Exception as e:
        app_logger.error(f"Feedback submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error submitting feedback"
        )


@router.get("", response_model=List[FeedbackResponse])
async def list_feedback(
    skip: int = 0,
    limit: int = 100,
    translation_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List feedback
    
    Admins can see all feedback, users can see their own
    """
    query = db.query(Feedback)
    
    if translation_id:
        query = query.filter(Feedback.translation_id == translation_id)
    
    if current_user.role != "admin":
        query = query.filter(Feedback.user_id == current_user.id)
    
    feedback_list = query.offset(skip).limit(limit).all()
    
    return feedback_list


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific feedback
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete feedback
    """
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(feedback)
    db.commit()
    
    app_logger.info(f"Feedback deleted: {feedback_id} by user {current_user.username}")
    
    return None

