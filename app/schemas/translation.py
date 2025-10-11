"""
Translation schemas
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from app.core.config import SUPPORTED_LANGUAGES


class TranslationRequest(BaseModel):
    """Schema for translation request"""
    file_id: Optional[int] = None
    text: Optional[str] = Field(None, max_length=50000)
    source_language: str = Field(..., min_length=2, max_length=10)
    target_languages: List[str] = Field(..., min_items=1)
    domain: Optional[str] = Field(None, description="Domain for context adaptation")
    apply_localization: bool = Field(default=True, description="Apply cultural localization")
    
    @validator("source_language")
    def validate_source_language(cls, v):
        if v not in SUPPORTED_LANGUAGES and v != "en":
            raise ValueError(f"Source language '{v}' not supported. Choose from 22 Indian languages or 'en'")
        return v
    
    @validator("target_languages")
    def validate_target_languages(cls, v):
        for lang in v:
            if lang not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Target language '{lang}' not supported. Choose from 22 Indian languages")
        return v


class TranslationResponse(BaseModel):
    """Schema for translation response"""
    id: int
    job_id: int
    source_language: str
    target_language: str
    source_text: Optional[str]
    translated_text: Optional[str]
    output_path: Optional[str]
    model_used: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LanguageDetectionResponse(BaseModel):
    """Schema for language detection response"""
    detected_language: str
    language_name: str
    confidence: float


class LocalizationRequest(BaseModel):
    """Schema for localization request"""
    translation_id: int
    domain: str
    cultural_context: Optional[dict] = None

