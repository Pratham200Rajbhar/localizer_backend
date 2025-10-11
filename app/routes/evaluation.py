"""
Evaluation route for BLEU/COMET scoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Optional
import time

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.evaluation import Evaluation
from app.models.translation import Translation
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.utils.logger import app_logger

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])


@router.post("/run", response_model=EvaluationResponse)
async def run_evaluation(
    evaluation_request: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compute BLEU/COMET score for translation evaluation
    
    Evaluates translation quality using standard metrics
    """
    try:
        # Get the translation to evaluate
        translation = db.query(Translation).filter(
            Translation.id == evaluation_request.translation_id
        ).first()
        
        if not translation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )
        
        app_logger.info(f"Running evaluation for translation {translation.id}")
        
        # Calculate BLEU score (simplified implementation)
        # In production, use SacreBLEU library
        bleu_score = calculate_bleu_score(
            reference=evaluation_request.reference_text,
            hypothesis=translation.translated_text
        )
        
        # Calculate COMET score (simplified implementation)
        # In production, use COMET library
        comet_score = calculate_comet_score(
            source=translation.source_text,
            hypothesis=translation.translated_text,
            reference=evaluation_request.reference_text
        )
        
        # Create evaluation record
        evaluation = Evaluation(
            translation_id=translation.id,
            bleu_score=bleu_score,
            comet_score=comet_score,
            reference_text=evaluation_request.reference_text,
            evaluator_id=current_user.id
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        app_logger.info(f"Evaluation completed: BLEU={bleu_score:.3f}, COMET={comet_score:.3f}")
        
        return EvaluationResponse(
            id=evaluation.id,
            translation_id=evaluation.translation_id,
            bleu_score=evaluation.bleu_score,
            comet_score=evaluation.comet_score,
            reference_text=evaluation.reference_text,
            evaluator_id=evaluation.evaluator_id,
            created_at=evaluation.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Evaluation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation failed"
        )


def calculate_bleu_score(reference: str, hypothesis: str) -> float:
    """
    Calculate BLEU score (simplified implementation)
    
    In production, use: from sacrebleu import sentence_bleu
    """
    # Simple word-level BLEU approximation
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    
    if not hyp_words:
        return 0.0
    
    # Count matching words
    matches = sum(1 for word in hyp_words if word in ref_words)
    precision = matches / len(hyp_words) if hyp_words else 0.0
    
    # Simple brevity penalty
    bp = min(1.0, len(hyp_words) / len(ref_words)) if ref_words else 0.0
    
    return precision * bp


def calculate_comet_score(source: str, hypothesis: str, reference: str) -> float:
    """
    Calculate COMET score (simplified implementation)
    
    In production, use the COMET library from Unbabel
    """
    # Simple semantic similarity approximation
    # In production, use actual COMET model
    ref_words = set(reference.lower().split())
    hyp_words = set(hypothesis.lower().split())
    
    if not ref_words and not hyp_words:
        return 1.0
    if not ref_words or not hyp_words:
        return 0.0
    
    intersection = len(ref_words & hyp_words)
    union = len(ref_words | hyp_words)
    
    return intersection / union if union > 0 else 0.0