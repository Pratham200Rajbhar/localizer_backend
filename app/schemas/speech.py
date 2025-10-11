"""
Speech (STT/TTS) schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from app.core.config import SUPPORTED_LANGUAGES


class STTRequest(BaseModel):
    """Schema for Speech-to-Text request"""
    file_id: Optional[int] = None
    language: Optional[str] = Field(None, description="Language hint for better transcription")
    
    @validator("language")
    def validate_language(cls, v):
        if v and v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{v}' not supported for STT")
        return v


class STTResponse(BaseModel):
    """Schema for STT response"""
    job_id: int
    transcript: str
    language_detected: str
    confidence: float
    output_path: str


class TTSRequest(BaseModel):
    """Schema for Text-to-Speech request"""
    text: str = Field(..., max_length=10000)
    language: str = Field(..., min_length=2, max_length=10)
    voice: Optional[str] = Field("default", description="Voice type: male/female/default")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    
    @validator("language")
    def validate_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{v}' not supported for TTS")
        return v


class TTSResponse(BaseModel):
    """Schema for TTS response"""
    job_id: int
    audio_path: str
    language: str
    duration: float
    format: str = "mp3"

