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

# Simple feedback router for direct /feedback endpoint
simple_router = APIRouter(tags=["Simple Feedback"])


@simple_router.post("/feedback")
async def submit_simple_feedback(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Simple feedback endpoint - saves rating/comments to storage/feedback.json
    Expected JSON: {"rating": 1-5, "comments": "optional"}
    """
    import json
    import os
    from datetime import datetime
    from pathlib import Path
    
    # Extract parameters from request
    rating = request.get("rating")
    comments = request.get("comments", "")
    
    # Validate rating
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating is required"
        )
    
    if not isinstance(rating, int) or not 1 <= rating <= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be an integer between 1 and 5"
        )
    
    try:
        # Create feedback entry
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id,
            "username": current_user.username,
            "rating": rating,
            "comments": comments
        }
        
        # Ensure storage directory exists
        storage_dir = Path("storage")
        storage_dir.mkdir(exist_ok=True)
        
        feedback_file = storage_dir / "feedback.json"
        
        # Load existing feedback or create new list
        feedback_list = []
        if feedback_file.exists():
            try:
                with open(feedback_file, "r") as f:
                    feedback_list = json.load(f)
            except json.JSONDecodeError:
                feedback_list = []
        
        # Add new feedback
        feedback_list.append(feedback_entry)
        
        # Save back to file
        with open(feedback_file, "w") as f:
            json.dump(feedback_list, f, indent=2)
        
        app_logger.info(f"Feedback saved: {rating} stars - {current_user.username}")
        
        return {
            "status": "success",
            "message": "Feedback saved successfully",
            "rating": rating,
            "comments": comments
        }
        
    except Exception as e:
        app_logger.error(f"Feedback save error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save feedback"
        )


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
    # Determine translation_id from either direct ID or file_id
    translation_id = feedback_data.translation_id
    
    if not translation_id and feedback_data.file_id:
        # Find most recent translation for this file
        translation = db.query(Translation).filter(Translation.file_id == feedback_data.file_id).first()
        if translation:
            translation_id = translation.id
        else:
            # Create a placeholder translation record for file-based feedback
            from app.models.file import File as FileModel
            file_record = db.query(FileModel).filter(FileModel.id == feedback_data.file_id).first()
            if not file_record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            # Create placeholder translation for feedback purposes
            placeholder_translation = Translation(
                user_id=current_user.id,
                file_id=feedback_data.file_id,
                source_language="en",
                target_language="hi",
                source_text=f"File: {file_record.filename}",
                translated_text="[Feedback on file]",
                model_used="feedback_placeholder",
                confidence_score=1.0,
                domain=file_record.domain or "general",
                duration=0.0
            )
            db.add(placeholder_translation)
            db.commit()
            db.refresh(placeholder_translation)
            translation_id = placeholder_translation.id
    
    if not translation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either translation_id or file_id must be provided"
        )
    
    try:
        # Create feedback
        feedback = Feedback(
            translation_id=translation_id,
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

