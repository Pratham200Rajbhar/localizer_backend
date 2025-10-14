# 🌐 API Endpoints Documentation
**Indian Language Localizer Backend - Frontend Developer Guide**

Base URL: `http://localhost:8000`

---

## 📋 Table of Contents
1. [Health & Monitoring](#health--monitoring)
2. [Content Management](#content-management)
3. [Translation Services](#translation-services)
4. [Speech Processing](#speech-processing)
5. [Video Localization](#video-localization)
6. [Assessment Translation](#assessment-translation)
7. [Job Management](#job-management)
8. [LMS Integration](#lms-integration)
9. [Feedback System](#feedback-system)

---

## 🏥 Health & Monitoring

### Check Service Health
```bash
curl -X GET http://localhost:8000/
```
**Response:**
```json
{
  "status": "healthy",
  "service": "Indian Language Localizer Backend",
  "version": "1.0.0",
  "environment": "production"
}
```

### Detailed Health Check
```bash
curl -X GET http://localhost:8000/health/detailed
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1729788123.456,
  "system": {
    "database": "connected",
    "storage": "available",
    "models": "loaded"
  },
  "services": {
    "translation": "operational",
    "speech": "operational",
    "video": "operational"
  }
}
```

### Get System Information
```bash
curl -X GET http://localhost:8000/system/info
```
**Response:**
```json
{
  "system": {
    "os": "Windows",
    "python_version": "3.10.9",
    "fastapi_version": "0.104.1"
  },
  "environment": "production",
  "supported_languages_count": 22
}
```

### Performance Metrics
```bash
curl -X GET http://localhost:8000/performance
```
**Response:**
```json
{
  "status": "ok",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 2048,
    "active_models": 3,
    "cache_size": 512
  }
}
```

---

## 📁 Content Management

### Upload File
```bash
curl -X POST http://localhost:8000/content/upload \
  -F "file=@document.txt" \
  -F "domain=general" \
  -F "source_language=en"
```
**Response:**
```json
{
  "id": 1,
  "filename": "document.txt",
  "size": 1024,
  "domain": "general",
  "source_language": "en",
  "path": "storage/uploads/unique-id/document.txt",
  "uploaded_at": "2025-10-14T10:30:00Z"
}
```

### Simple Upload (Alternative Endpoint)
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.txt"
```
**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "filename": "document.txt",
  "size": 1024
}
```

### List Files
```bash
curl -X GET "http://localhost:8000/content/files?skip=0&limit=10"
```
**Response:**
```json
[
  {
    "id": 1,
    "filename": "document.txt",
    "size": 1024,
    "domain": "general",
    "source_language": "en",
    "uploaded_at": "2025-10-14T10:30:00Z"
  }
]
```

### Get File Details
```bash
curl -X GET http://localhost:8000/content/files/1
```
**Response:**
```json
{
  "id": 1,
  "filename": "document.txt",
  "size": 1024,
  "domain": "general",
  "source_language": "en",
  "path": "storage/uploads/unique-id/document.txt",
  "uploaded_at": "2025-10-14T10:30:00Z"
}
```

### Delete File
```bash
curl -X DELETE http://localhost:8000/content/files/1
```
**Response:** `204 No Content`

---

## 🌐 Translation Services

### Get Supported Languages
```bash
curl -X GET http://localhost:8000/supported-languages
```
**Response:**
```json
{
  "supported_languages": {
    "as": "Assamese",
    "bn": "Bengali",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu"
  },
  "total_count": 22,
  "source_languages": ["en", "auto"]
}
```

### Detect Language
```bash
curl -X POST http://localhost:8000/detect-language \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?"}'
```
**Response:**
```json
{
  "detected_language": "en",
  "confidence": 0.95,
  "supported": true
}
```

### Translate Text
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, welcome to our vocational training program",
    "source_language": "en",
    "target_languages": ["hi", "bn"],
    "domain": "education",
    "apply_localization": true
  }'
```
**Response:**
```json
{
  "source_text": "Hello, welcome to our vocational training program",
  "source_language": "en",
  "results": [
    {
      "target_language": "hi",
      "translated_text": "नमस्ते, हमारे व्यावसायिक प्रशिक्षण कार्यक्रम में आपका स्वागत है",
      "confidence": 0.92,
      "processing_time": 1.2
    },
    {
      "target_language": "bn",
      "translated_text": "হ্যালো, আমাদের বৃত্তিমূলক প্রশিক্ষণ প্রোগ্রামে স্বাগতম",
      "confidence": 0.89,
      "processing_time": 1.1
    }
  ],
  "total_processing_time": 2.3,
  "localized": true
}
```

### Translate File
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "source_language": "en",
    "target_languages": ["hi", "ta"],
    "domain": "healthcare",
    "apply_localization": true
  }'
```
**Response:**
```json
{
  "file_id": 1,
  "source_language": "en",
  "results": [
    {
      "target_language": "hi",
      "output_file": "storage/outputs/file_1_hi.txt",
      "translated_text": "स्वास्थ्य सेवा प्रशिक्षण सामग्री...",
      "confidence": 0.91,
      "processing_time": 3.5
    }
  ],
  "total_processing_time": 7.1
}
```

### Apply Localization
```bash
curl -X POST http://localhost:8000/localize/context \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Safety equipment is mandatory",
    "source_language": "en",
    "target_language": "hi",
    "domain": "construction"
  }'
```
**Response:**
```json
{
  "original_text": "Safety equipment is mandatory",
  "localized_text": "सुरक्षा उपकरण अनिवार्य है",
  "cultural_adaptations": [
    "Added formal tone for workplace context",
    "Used construction-specific terminology"
  ],
  "domain": "construction"
}
```

### Translation Statistics
```bash
curl -X GET http://localhost:8000/stats
```
**Response:**
```json
{
  "total_translations": 1245,
  "translations_by_language": {
    "hi": 450,
    "bn": 320,
    "ta": 275
  },
  "supported_languages_count": 22,
  "average_processing_time": 2.1,
  "most_translated_domain": "education"
}
```

### Translation History
```bash
curl -X GET http://localhost:8000/history/1
```
**Response:**
```json
{
  "file_id": 1,
  "filename": "document.txt",
  "translations": [
    {
      "id": 1,
      "target_language": "hi",
      "created_at": "2025-10-14T10:35:00Z",
      "status": "completed",
      "output_file": "storage/outputs/file_1_hi.txt"
    }
  ],
  "total_translations": 1
}
```

---

## 🗣️ Speech Processing

### Speech-to-Text (STT)
```bash
curl -X POST http://localhost:8000/speech/stt \
  -F "file=@audio.mp3" \
  -F "language=hi"
```
**Response:**
```json
{
  "transcript": "नमस्ते, यह एक परीक्षण ऑडियो है",
  "language": "hi",
  "confidence": 0.87,
  "processing_time": 5.2,
  "audio_duration": 10.5
}
```

### Text-to-Speech (TTS)
```bash
curl -X POST http://localhost:8000/speech/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "स्वागत है व्यावसायिक प्रशिक्षण में",
    "language": "hi",
    "voice_speed": 1.0,
    "output_format": "mp3"
  }'
```
**Response:**
```json
{
  "status": "success",
  "output_file": "storage/outputs/tts_output_12345.mp3",
  "duration": 3.2,
  "language": "hi",
  "processing_time": 2.1
}
```

### Audio Localization
```bash
curl -X POST http://localhost:8000/speech/localize \
  -F "file=@audio.mp3" \
  -F "target_language=hi" \
  -F "domain=general"
```
**Response:**
```json
{
  "status": "success",
  "pipeline_steps": {
    "stt": "completed",
    "translation": "completed",
    "tts": "completed"
  },
  "output_file": "storage/outputs/localized_audio_12345.mp3",
  "original_text": "Welcome to the training program",
  "translated_text": "प्रशिक्षण कार्यक्रम में आपका स्वागत है",
  "processing_time": 15.3
}
```

### Generate Subtitles
```bash
curl -X POST http://localhost:8000/speech/subtitles \
  -F "file=@video.mp4" \
  -F "language=en" \
  -F "format=srt"
```
**Response:**
```json
{
  "status": "success",
  "subtitle_file": "storage/outputs/subtitles_12345.srt",
  "format": "srt",
  "transcript": "Welcome to our training. This session covers...",
  "processing_time": 8.7
}
```

### Download Audio
```bash
curl -X GET http://localhost:8000/speech/download/audio_12345.mp3 \
  --output downloaded_audio.mp3
```
**Response:** Binary audio file

---

## 🎥 Video Localization

### Video Localization
```bash
curl -X POST http://localhost:8000/video/localize \
  -F "file=@training_video.mp4" \
  -F "target_language=hi" \
  -F "domain=healthcare" \
  -F "include_subtitles=true" \
  -F "include_dubbed_audio=false"
```
**Response:**
```json
{
  "status": "success",
  "outputs": {
    "subtitles": "storage/outputs/video_subtitles_12345.srt",
    "transcript": "storage/outputs/video_transcript_12345.txt"
  },
  "processing_details": {
    "original_duration": 120.5,
    "audio_extracted": true,
    "subtitles_generated": true,
    "dubbing_applied": false
  },
  "processing_time": 180.2
}
```

### Extract Audio from Video
```bash
curl -X POST http://localhost:8000/video/extract-audio \
  -F "file=@video.mp4" \
  -F "output_format=wav"
```
**Response:**
```json
{
  "status": "success",
  "audio_file": "storage/outputs/extracted_audio_12345.wav",
  "original_video": "video.mp4",
  "audio_duration": 120.5,
  "processing_time": 15.3
}
```

### Download Video Output
```bash
curl -X GET http://localhost:8000/video/download/video_output_12345.mp4 \
  --output localized_video.mp4
```
**Response:** Binary video file

---

## 📚 Assessment Translation

### Translate Assessment
```bash
curl -X POST http://localhost:8000/assessment/translate \
  -F "file=@quiz.json" \
  -F "target_language=hi" \
  -F "domain=education"
```
**Response:**
```json
{
  "status": "success",
  "output_file": "storage/outputs/quiz_hi_12345.json",
  "questions_translated": 15,
  "processing_time": 12.8,
  "translation_summary": {
    "questions": 15,
    "options": 60,
    "instructions": 1
  }
}
```

### Validate Assessment Format
```bash
curl -X POST http://localhost:8000/assessment/validate \
  -F "file=@assessment.json"
```
**Response:**
```json
{
  "status": "valid",
  "format": "json",
  "structure": {
    "questions": 10,
    "question_types": ["multiple_choice", "text"],
    "has_instructions": true,
    "has_time_limit": true
  },
  "validation_details": {
    "required_fields": "present",
    "format_compliance": "valid"
  }
}
```

### Get Sample Assessment Formats
```bash
curl -X GET http://localhost:8000/assessment/sample-formats
```
**Response:**
```json
{
  "json_sample": {
    "assessment": {
      "title": "Sample Mathematics Quiz",
      "instructions": "Answer all questions",
      "questions": [
        {
          "id": 1,
          "type": "multiple_choice",
          "question": "What is 2 + 2?",
          "options": ["3", "4", "5", "6"],
          "correct_answer": "4"
        }
      ]
    }
  },
  "csv_sample_structure": {
    "headers": ["id", "question", "option_a", "option_b", "correct_answer"],
    "description": "CSV format for assessments"
  }
}
```

### Download Assessment
```bash
curl -X GET http://localhost:8000/assessment/download/quiz_hi_12345.json \
  --output translated_quiz.json
```
**Response:** JSON assessment file

---

## ⚙️ Job Management

### Trigger Model Retraining
```bash
curl -X POST "http://localhost:8000/jobs/retrain?domain=healthcare&model_type=indicTrans2&epochs=3"
```
**Response:**
```json
{
  "job_id": "retrain_healthcare_12345",
  "status": "started",
  "message": "Model retraining initiated",
  "parameters": {
    "domain": "healthcare",
    "model_type": "indicTrans2",
    "epochs": 3,
    "batch_size": 16
  },
  "estimated_time": "45 minutes"
}
```

### Get Job Status
```bash
curl -X GET http://localhost:8000/jobs/retrain_healthcare_12345
```
**Response:**
```json
{
  "job_id": "retrain_healthcare_12345",
  "status": "running",
  "progress": 65,
  "current_epoch": 2,
  "elapsed_time": 1800,
  "estimated_remaining": 1080,
  "logs": [
    "Starting epoch 2/3",
    "Training loss: 0.245",
    "Validation accuracy: 0.89"
  ]
}
```

### List Active Jobs
```bash
curl -X GET http://localhost:8000/jobs
```
**Response:**
```json
{
  "jobs": [
    {
      "job_id": "retrain_healthcare_12345",
      "status": "running",
      "type": "model_retraining",
      "started_at": "2025-10-14T10:00:00Z",
      "progress": 65
    }
  ],
  "total": 1
}
```

### Cancel Job
```bash
curl -X DELETE http://localhost:8000/jobs/retrain_healthcare_12345
```
**Response:**
```json
{
  "message": "Job cancelled successfully",
  "job_id": "retrain_healthcare_12345",
  "status": "cancelled"
}
```

---

## 🏢 LMS Integration

### Integration Upload
```bash
curl -X POST http://localhost:8000/integration/upload \
  -F "file=@course_material.txt" \
  -F "target_languages=hi,bn,ta" \
  -F "content_type=document" \
  -F "domain=general" \
  -F "partner_id=lms_partner_123" \
  -F "priority=normal"
```
**Response:**
```json
{
  "job_id": "integration_12345",
  "status": "queued",
  "content_type": "document",
  "target_languages": ["hi", "bn", "ta"],
  "estimated_completion": "2025-10-14T11:15:00Z",
  "partner_id": "lms_partner_123"
}
```

### Get Integration Results
```bash
curl -X GET http://localhost:8000/integration/results/integration_12345
```
**Response:**
```json
{
  "job_id": "integration_12345",
  "status": "completed",
  "results": [
    {
      "language": "hi",
      "output_file": "storage/outputs/integration_12345_hi.txt",
      "status": "success",
      "quality_score": 0.89
    },
    {
      "language": "bn",
      "output_file": "storage/outputs/integration_12345_bn.txt",
      "status": "success",
      "quality_score": 0.85
    }
  ],
  "completion_time": "2025-10-14T11:12:00Z",
  "total_processing_time": 720
}
```

### Submit Integration Feedback
```bash
curl -X POST http://localhost:8000/integration/feedback \
  -F "job_id=integration_12345" \
  -F "partner_id=lms_partner_123" \
  -F "quality_rating=4" \
  -F "accuracy_rating=5" \
  -F "feedback_comments=Excellent translation quality for technical content"
```
**Response:**
```json
{
  "status": "success",
  "job_id": "integration_12345",
  "message": "Feedback recorded successfully",
  "feedback_id": "feedback_789"
}
```

### Download Integration Output
```bash
curl -X GET "http://localhost:8000/integration/download/integration_12345_hi.txt?partner_id=lms_partner_123" \
  --output translated_content.txt
```
**Response:** Translated file content

### Integration Service Status
```bash
curl -X GET http://localhost:8000/integration/status
```
**Response:**
```json
{
  "service_status": "operational",
  "api_version": "1.0",
  "service_capabilities": {
    "max_file_size_mb": 100,
    "supported_formats": ["txt", "pdf", "docx", "json", "csv", "mp3", "mp4"],
    "processing_types": {
      "document": "Text document translation",
      "assessment": "Educational assessment localization",
      "audio": "Speech localization with STT/TTS",
      "video": "Video localization with subtitles"
    },
    "supported_languages": 22,
    "concurrent_jobs": 10
  }
}
```

---

## 💬 Feedback System

### Submit Simple Feedback
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "comments": "Translation quality is very good for technical content"
  }'
```
**Response:**
```json
{
  "status": "success",
  "message": "Feedback saved successfully",
  "feedback_id": "feedback_456",
  "timestamp": "2025-10-14T12:00:00Z"
}
```

### Submit Detailed Feedback
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "rating": 5,
    "comments": "Excellent cultural localization",
    "accuracy_rating": 5,
    "cultural_appropriateness": 4,
    "corrections": {
      "original": "safety equipment",
      "suggested": "सुरक्षा उपकरण"
    }
  }'
```
**Response:**
```json
{
  "id": 123,
  "file_id": 1,
  "rating": 5,
  "comments": "Excellent cultural localization",
  "accuracy_rating": 5,
  "cultural_appropriateness": 4,
  "created_at": "2025-10-14T12:00:00Z",
  "status": "submitted"
}
```

### List Feedback
```bash
curl -X GET "http://localhost:8000/feedback?skip=0&limit=10&translation_id=1"
```
**Response:**
```json
[
  {
    "id": 123,
    "file_id": 1,
    "rating": 5,
    "comments": "Excellent translation",
    "created_at": "2025-10-14T12:00:00Z"
  }
]
```

### Get Specific Feedback
```bash
curl -X GET http://localhost:8000/feedback/123
```
**Response:**
```json
{
  "id": 123,
  "file_id": 1,
  "rating": 5,
  "comments": "Excellent cultural localization",
  "accuracy_rating": 5,
  "cultural_appropriateness": 4,
  "created_at": "2025-10-14T12:00:00Z"
}
```

---

## 🔍 Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid target language 'xyz'. Choose from 22 Indian languages."
}
```

**404 Not Found:**
```json
{
  "detail": "File not found"
}
```

**413 Request Entity Too Large:**
```json
{
  "detail": "File size exceeds 100MB limit"
}
```

**415 Unsupported Media Type:**
```json
{
  "detail": "File format not supported. Allowed: .txt, .pdf, .mp3, .mp4"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "target_languages"],
      "msg": "Target language 'xyz' not supported",
      "type": "value_error"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "error": "Translation service temporarily unavailable",
  "message": "Please try again later"
}
```

---

## 📝 Notes for Frontend Developers

### File Upload Requirements
- **Max file size:** 100MB for documents, 500MB for videos
- **Supported formats:** .txt, .pdf, .docx, .mp3, .mp4, .wav, .json, .csv
- **Always use multipart/form-data** for file uploads

### Language Codes
Use ISO language codes for the 22 supported Indian languages:
- `hi` (Hindi), `bn` (Bengali), `ta` (Tamil), `te` (Telugu)
- `gu` (Gujarati), `mr` (Marathi), `kn` (Kannada), `ml` (Malayalam)
- `as` (Assamese), `or` (Odia), `pa` (Punjabi), `ur` (Urdu)
- And 10 more regional languages

### Rate Limiting
- No authentication required for basic operations
- Consider implementing client-side rate limiting for better UX
- Large file processing may take several minutes

### Async Operations
- File translation, video processing, and model retraining are asynchronous
- Use job IDs to poll for completion status
- Implement progress indicators for better user experience

### Error Handling
- Always check response status codes
- Implement retry logic for 5xx errors
- Validate file types and sizes before upload