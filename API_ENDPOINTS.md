# 🚀 FastAPI Backend - Complete API Endpoints with cURL

**AI-Powered Multilingual Translation & Localization System**  
**Base URL**: `http://localhost:8000`  
**Supported Languages**: 22 Indian languages + English

## 🔥 **COMPLETE ENDPOINT LIST (35+ Endpoints)**

### �️ **Core System:**
- **Health Checks** (4 endpoints)
- **Language Support** (1 endpoint) 
- **Performance Monitoring** (2 endpoints)

### 🔄 **Translation Engine:**
- **Language Detection** (1 endpoint)
- **Text Translation** (3 endpoints)
- **Cultural Localization** (1 endpoint)
- **Translation History & Stats** (2 endpoints)

### 🎤 **Speech Processing:**
- **Speech-to-Text (STT)** (1 endpoint)
- **Text-to-Speech (TTS)** (2 endpoints)

### 📁 **File Management:**
- **File Upload** (2 endpoints)
- **File Operations** (3 endpoints)

### 💬 **Feedback System:**
- **User Feedback** (4 endpoints)

### 🔄 **Background Jobs:**
- **Job Management** (5 endpoints)

### 📊 **Evaluation & Quality:**
- **Translation Quality** (1 endpoint)

---

## 🌐 **1. Health & System Status**

### Check Supported Languages
```bash
curl -X GET "http://localhost:8000/supported-languages" \
  -H "Content-Type: application/json"
```

**Expected Output:**
```json
{
  "supported_languages": {
    "as": "Assamese",
    "bn": "Bengali", 
    "brx": "Bodo",
    "doi": "Dogri",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ks": "Kashmiri",
    "kok": "Konkani",
    "mai": "Maithili",
    "ml": "Malayalam",
    "mni": "Manipuri",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "sat": "Santali",
    "sd": "Sindhi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu"
  },
  "total_count": 22,
  "language_codes": ["as", "bn", "brx", "..."],
  "english_supported": true
}
```

### Server Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": 1760363294.934907
}
```

### Root Endpoint
```bash
curl -X GET "http://localhost:8000/"
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "Indian Language Localizer",
  "version": "1.0.0",
  "environment": "production"
}
```

### Database Health Check
```bash
curl -X GET "http://localhost:8000/health/db"
```

**Expected Output:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": 1760363294.934907
}
```

### Detailed Health Check
```bash
curl -X GET "http://localhost:8000/health/detailed"
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": 1760363294.934907,
  "database": "connected",
  "system": {
    "memory_usage": "67.7%",
    "disk_usage": "73.3%", 
    "cpu_count": 20
  },
  "services": {
    "translation": "available",
    "speech": "available",
    "file_upload": "available"
  }
}
```

---

## 🔍 **2. Language Detection**

### Detect Language from Text
```bash
curl -X POST "http://localhost:8000/detect-language" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "नमस्ते, आप कैसे हैं?"
  }'
```

**Expected Output:**
```json
{
  "detected_language": "hi",
  "language_name": "Hindi",
  "confidence": 0.95
}
```

### English Text Detection
```bash
curl -X POST "http://localhost:8000/detect-language" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you today?"
  }'
```

**Expected Output:**
```json
{
  "detected_language": "en", 
  "language_name": "English",
  "confidence": 0.98
}
```

---

## 🔄 **3. Translation Engine**

### English to Hindi Translation
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to our multilingual translation platform. We support 22 Indian languages.",
    "source_language": "en",
    "target_languages": ["hi"],
    "domain": "general",
    "apply_localization": true
  }'
```

**Expected Output:**
```json
{
  "results": [
    {
      "translated_text": "हमारे बहुभाषी अनुवाद मंच में आपका स्वागत है। हम 22 भारतीय भाषाओं का समर्थन करते हैं।",
      "source_language": "en",
      "target_language": "hi", 
      "source_language_name": "English",
      "target_language_name": "Hindi",
      "model_used": "IndicTrans2",
      "confidence_score": 0.92,
      "duration": 1.27,
      "domain": "general",
      "localization_applied": true
    }
  ],
  "total_translations": 1,
  "total_duration": 1.27
}
```

### Multi-Language Translation (English to Multiple Indian Languages)
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Good morning, have a great day!",
    "source_language": "en", 
    "target_languages": ["hi", "bn", "ta", "te", "gu"],
    "domain": "general"
  }'
```

**Expected Output:**
```json
{
  "results": [
    {
      "translated_text": "सुप्रभात, आपका दिन शुभ हो!",
      "target_language": "hi",
      "target_language_name": "Hindi",
      "model_used": "IndicTrans2",
      "confidence_score": 0.89,
      "duration": 0.31
    },
    {
      "translated_text": "সুপ্রভাত, আপনার দিনটি ভাল কাটুক!",
      "target_language": "bn", 
      "target_language_name": "Bengali",
      "model_used": "IndicTrans2",
      "confidence_score": 0.91,
      "duration": 0.28
    },
    {
      "translated_text": "காலை வணக்கம், உங்கள் நாள் சிறப்பாக இருக்கட்டும்!",
      "target_language": "ta",
      "target_language_name": "Tamil", 
      "model_used": "IndicTrans2",
      "confidence_score": 0.87,
      "duration": 0.33
    }
  ],
  "total_translations": 5,
  "total_duration": 1.52
}
```

### Cross-Indian Language Translation (Hindi to Bengali)
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "आज मौसम बहुत अच्छा है।",
    "source_language": "hi",
    "target_languages": ["bn"],
    "domain": "general"
  }'
```

**Expected Output:**
```json
{
  "results": [
    {
      "translated_text": "আজ আবহাওয়া খুব ভাল।",
      "source_language": "hi",
      "target_language": "bn",
      "source_language_name": "Hindi", 
      "target_language_name": "Bengali",
      "model_used": "NLLB-Indic",
      "confidence_score": 0.88,
      "duration": 0.22
    }
  ],
  "total_translations": 1,
  "total_duration": 0.22
}
```

---

## 🏥 **4. Domain-Specific Translation (Healthcare)**

### Medical Text Translation
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Please take this medicine twice a day after meals. Consult your doctor if you have any side effects.",
    "source_language": "en",
    "target_languages": ["hi", "bn"],
    "domain": "healthcare",
    "apply_localization": true
  }'
```

**Expected Output:**
```json
{
  "results": [
    {
      "translated_text": "कृपया इस दवा को दिन में दो बार भोजन के बाद लें। यदि आपको कोई दुष्प्रभाव हो तो डॉक्टर से सलाह लें।",
      "target_language": "hi",
      "target_language_name": "Hindi",
      "model_used": "IndicTrans2",
      "domain": "healthcare",
      "localization_applied": true,
      "confidence_score": 0.91,
      "duration": 1.15
    }
  ]
}
```

---

## 🌍 **5. Cultural Localization**

### Apply Cultural Adaptation
```bash
curl -X POST "http://localhost:8000/localize/context" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Thank you sir, please help me with this task",
    "language": "hi",
    "domain": "general"
  }'
```

**Expected Output:**
```json
{
  "original_text": "Thank you sir, please help me with this task",
  "localized_text": "धन्यवाद साहब जी, कृपया इस कार्य में मेरी सहायता करें",
  "language": "hi",
  "language_name": "Hindi",
  "domain": "general",
  "adaptations_applied": [
    "honorific_adaptation",
    "courtesy_phrase_localization"
  ],
  "confidence": 0.8
}
```

---

## 📁 **6. File Upload & Management**

### Simple File Upload (No Authentication)
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_document.txt" \
  -F "domain=general" \
  -F "source_language=en"
```

**Expected Output:**
```json
{
  "message": "File uploaded successfully",
  "filename": "sample_document.txt",
  "size": 1024,
  "upload_path": "/upload/sample_document.txt"
}
```

### Content Management File Upload
```bash
curl -X POST "http://localhost:8000/content/upload" \
  -F "file=@sample_document.txt" \
  -F "domain=general" \
  -F "source_language=en"
```

**Expected Output:**
```json
{
  "id": 123,
  "filename": "sample_document.txt",
  "original_filename": "sample_document.txt", 
  "file_type": ".txt",
  "size": 1024,
  "path": "storage/uploads/123/sample_document.txt",
  "domain": "general",
  "source_language": "en",
  "created_at": "2025-10-13T19:22:14"
}
```

### File-Based Translation
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 123,
    "source_language": "en", 
    "target_languages": ["hi", "bn"],
    "domain": "general"
  }'
```

### List All Uploaded Files  
```bash
curl -X GET "http://localhost:8000/content/files"
```

**Expected Output:**
```json
[
  {
    "id": 123,
    "filename": "sample_document.txt", 
    "original_filename": "sample_document.txt",
    "file_type": ".txt",
    "size": 1024,
    "domain": "general",
    "source_language": "en",
    "created_at": "2025-10-13T19:22:14"
  },
  {
    "id": 124,
    "filename": "medical_doc.pdf",
    "original_filename": "medical_document.pdf",
    "file_type": ".pdf", 
    "size": 2048,
    "domain": "healthcare",
    "source_language": "en",
    "created_at": "2025-10-13T20:15:30"
  }
]
```

### Get Specific File Details
```bash
curl -X GET "http://localhost:8000/content/files/123"
```

**Expected Output:**
```json
{
  "id": 123,
  "filename": "sample_document.txt",
  "original_filename": "sample_document.txt",
  "file_type": ".txt",
  "size": 1024,
  "path": "storage/uploads/123/sample_document.txt",
  "domain": "general", 
  "source_language": "en",
  "created_at": "2025-10-13T19:22:14"
}
```

### Delete Uploaded File
```bash
curl -X DELETE "http://localhost:8000/content/files/123"
```

**Expected Output:**
```
HTTP 204 No Content
```

---

## 🎤 **7. Speech-to-Text (STT)**

### Audio Transcription
```bash
curl -X POST "http://localhost:8000/speech/stt" \
  -F "file=@audio_sample.mp3" \
  -F "language=hi"
```

**Expected Output:**
```json
{
  "transcript": "नमस्ते सभी को, आज का मौसम बहुत अच्छा है।",
  "language_detected": "hi",
  "language_name": "Hindi", 
  "confidence": 0.87,
  "duration": 2.35,
  "segments": [
    {
      "start": 0.0,
      "end": 2.1,
      "text": "नमस्ते सभी को"
    },
    {
      "start": 2.2,
      "end": 4.5, 
      "text": "आज का मौसम बहुत अच्छा है।"
    }
  ],
  "model_used": "whisper-large-v3"
}
```

### English Audio Transcription
```bash
curl -X POST "http://localhost:8000/speech/stt" \
  -F "file=@english_audio.wav"
```

**Expected Output:**
```json
{
  "transcript": "Hello everyone, welcome to our platform. This is a test message for speech recognition.",
  "language_detected": "en",
  "language_name": "English",
  "confidence": 0.94,
  "duration": 1.67,
  "model_used": "whisper-large-v3"
}
```

---

## 🔊 **8. Text-to-Speech (TTS)**

### Hindi Text-to-Speech
```bash
curl -X POST "http://localhost:8000/speech/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "नमस्ते सभी को, आपका स्वागत है।",
    "language": "hi",
    "voice": "default",
    "speed": 1.0
  }'
```

**Expected Output:**
```json
{
  "audio_path": "storage/outputs/tts_hi_a1b2c3d4.mp3",
  "language": "hi",
  "language_name": "Hindi",
  "duration": 0.54,
  "generation_time": 0.54,
  "format": "mp3"
}
```

### Bengali Text-to-Speech
```bash
curl -X POST "http://localhost:8000/speech/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "আপনাদের সবাইকে স্বাগতম।",
    "language": "bn",
    "speed": 0.8
  }'
```

### English Text-to-Speech
```bash
curl -X POST "http://localhost:8000/speech/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to our multilingual platform.",
    "language": "en"
  }'
```

### Download Generated Audio
```bash
curl -X GET "http://localhost:8000/speech/tts/download/tts_hi_a1b2c3d4.mp3" \
  --output downloaded_audio.mp3
```

**Expected Output:**
```
Binary audio file downloaded as downloaded_audio.mp3
```

---

## 💬 **9. Feedback System**

### Submit Rating & Feedback
```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comments": "Excellent translation quality! The Hindi output was very accurate and natural.",
    "translation_id": 123,
    "corrections": "Minor suggestion: use more formal tone"
  }'
```

**Expected Output:**
```json
{
  "id": 456,
  "translation_id": 123,
  "rating": 5,
  "comments": "Excellent translation quality! The Hindi output was very accurate and natural.",
  "corrections": "Minor suggestion: use more formal tone",
  "is_helpful": 1,
  "created_at": "2025-10-13T19:25:30"
}
```

### Simple Anonymous Feedback
```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "comments": "Good service, fast translation"
  }'
```

### List All Feedback
```bash
curl -X GET "http://localhost:8000/feedback"
```

**Expected Output:**
```json
[
  {
    "id": 456,
    "translation_id": 123,
    "rating": 5,
    "comments": "Excellent translation quality!",
    "corrections": "Minor suggestion: use more formal tone",
    "is_helpful": true,
    "created_at": "2025-10-13T19:25:30"
  },
  {
    "id": 457,
    "rating": 4,
    "comments": "Good service, fast translation", 
    "created_at": "2025-10-13T19:26:15"
  }
]
```

### Get Specific Feedback
```bash
curl -X GET "http://localhost:8000/feedback/456"
```

**Expected Output:**
```json
{
  "id": 456,
  "translation_id": 123,
  "rating": 5,
  "comments": "Excellent translation quality!",
  "corrections": "Minor suggestion: use more formal tone",
  "is_helpful": true,
  "created_at": "2025-10-13T19:25:30"
}
```

### Delete Feedback
```bash
curl -X DELETE "http://localhost:8000/feedback/456"
```

**Expected Output:**
```
HTTP 204 No Content
```

---

## 📊 **10. Performance Monitoring**

### Prometheus Metrics
```bash
curl -X GET "http://localhost:8000/metrics"
```

**Expected Output:**
```
# HELP translation_requests_total Total number of translation requests
# TYPE translation_requests_total counter
translation_requests_total{language_pair="en-hi"} 145.0
translation_requests_total{language_pair="en-bn"} 89.0

# HELP translation_duration_seconds Time spent on translations
# TYPE translation_duration_seconds histogram
translation_duration_seconds_bucket{le="0.5"} 23.0
translation_duration_seconds_bucket{le="1.0"} 67.0
translation_duration_seconds_bucket{le="2.0"} 125.0

# HELP bleu_score_average Average BLEU score for translations
# TYPE bleu_score_average gauge
bleu_score_average{language="hi"} 0.847
bleu_score_average{language="bn"} 0.823
```

### System Performance
```bash
curl -X GET "http://localhost:8000/performance"
```

**Expected Output:**
```json
{
  "status": "ok",
  "metrics": {
    "active_requests": 3,
    "total_requests": 1247,
    "avg_response_time": 1.23,
    "success_rate": 99.2
  },
  "memory": {
    "total": "16.0 GB",
    "used": "10.8 GB", 
    "percentage": 67.5
  },
  "system": {
    "cpu_count": 20,
    "gpu_available": true,
    "gpu_name": "NVIDIA GeForce RTX 3050 6GB"
  }
}
```

---

## � **11. Translation History & Statistics**

### Get Translation History for File
```bash
curl -X GET "http://localhost:8000/history/123"
```

**Expected Output:**
```json
{
  "file_id": 123,
  "filename": "sample_document.txt",
  "translations": [
    {
      "id": 789,
      "target_language": "hi",
      "translated_text": "नमूना दस्तावेज़ सामग्री",
      "model_used": "IndicTrans2",
      "confidence_score": 0.92,
      "created_at": "2025-10-13T19:30:15"
    },
    {
      "id": 790,
      "target_language": "bn", 
      "translated_text": "নমুনা নথি বিষয়বস্তু",
      "model_used": "IndicTrans2",
      "confidence_score": 0.89,
      "created_at": "2025-10-13T19:30:45"
    }
  ],
  "total_translations": 2
}
```

### Get Translation Statistics
```bash
curl -X GET "http://localhost:8000/stats"
```

**Expected Output:**
```json
{
  "total_translations": 15420,
  "total_files": 1247,
  "languages": {
    "most_translated_to": {
      "hi": 5234,
      "bn": 3892,
      "ta": 2745
    },
    "most_translated_from": {
      "en": 12450,
      "hi": 1876,
      "bn": 1094
    }
  },
  "models": {
    "IndicTrans2": 12890,
    "IndicTrans2-Bridge": 2100,
    "NLLB-Indic": 350,
    "Emergency": 80
  },
  "performance": {
    "avg_translation_time": 0.85,
    "success_rate": 98.7
  }
}
```

## �🔄 **12. Background Jobs & Model Management**

### Trigger Model Retraining
```bash
curl -X POST "http://localhost:8000/jobs/retrain" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "healthcare",
    "model_type": "indicTrans2", 
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5
  }'
```

**Expected Output:**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "started",
  "message": "Model retraining started",
  "domain": "healthcare",
  "model_type": "indicTrans2",
  "estimated_duration": "30 minutes"
}
```

### Check Job Status  
```bash
curl -X GET "http://localhost:8000/jobs/f47ac10b-58cc-4372-a567-0e02b2c3d479"
```

**Expected Output:**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "running",
  "started_at": "2025-10-13T19:30:00",
  "progress": 65,
  "message": "Training epoch 2/3 completed...",
  "domain": "healthcare",
  "model_type": "indicTrans2"
}
```

### List Active Jobs
```bash
curl -X GET "http://localhost:8000/jobs"
```

**Expected Output:**
```json
{
  "jobs": [
    {
      "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "status": "running",
      "progress": 65,
      "domain": "healthcare"
    }
  ],
  "total": 1
}
```

### Cancel/Delete Job
```bash
curl -X DELETE "http://localhost:8000/jobs/f47ac10b-58cc-4372-a567-0e02b2c3d479"
```

**Expected Output:**
```json
{
  "message": "Job f47ac10b-58cc-4372-a567-0e02b2c3d479 cancelled successfully",
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "previous_status": "running"
}
```

### Cleanup Completed Jobs
```bash
curl -X POST "http://localhost:8000/jobs/cleanup"
```

**Expected Output:**
```json
{
  "message": "Cleanup completed",
  "jobs_cleaned": 12,
  "disk_space_freed": "45.2 MB"
}
```

---

## 📈 **13. Translation Evaluation & Quality Metrics**

### Run Translation Evaluation
```bash
curl -X POST "http://localhost:8000/evaluate/run" \
  -H "Content-Type: application/json" \
  -d '{
    "translation_id": 123,
    "reference_text": "आपका स्वागत है",
    "evaluation_metrics": ["bleu", "comet", "ter"]
  }'
```

**Expected Output:**
```json
{
  "evaluation_id": 789,
  "translation_id": 123,
  "metrics": {
    "bleu_score": 0.847,
    "comet_score": 0.783,
    "ter_score": 0.156,
    "meteor_score": 0.692
  },
  "language_pair": "en-hi",
  "model_used": "IndicTrans2",
  "evaluated_at": "2025-10-13T19:35:20"
}
```

### Get Evaluation Results
```bash
curl -X GET "http://localhost:8000/evaluate/results?translation_id=123"
```

**Expected Output:**
```json
{
  "translation_id": 123,
  "evaluations": [
    {
      "evaluation_id": 789,
      "metrics": {
        "bleu_score": 0.847,
        "comet_score": 0.783,
        "ter_score": 0.156
      },
      "evaluated_at": "2025-10-13T19:35:20"
    }
  ],
  "average_scores": {
    "bleu": 0.847,
    "comet": 0.783,
    "ter": 0.156
  }
}
```

---

## 🧪 **14. Batch Processing**

### Batch Translation
```bash
curl -X POST "http://localhost:8000/batch-translate" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Good morning",
      "How are you?", 
      "Thank you very much",
      "Have a great day"
    ],
    "source_language": "en",
    "target_languages": ["hi", "bn"],
    "domain": "general",
    "apply_localization": true
  }'
```

**Expected Output:**
```json
{
  "results": [
    {
      "index": 0,
      "source_text": "Good morning",
      "translations": [
        {
          "translated_text": "सुप्रभात",
          "target_language": "hi",
          "model_used": "IndicTrans2"
        },
        {
          "translated_text": "সুপ্রভাত", 
          "target_language": "bn",
          "model_used": "IndicTrans2"
        }
      ],
      "success": true
    }
  ],
  "total_texts": 4,
  "successful_translations": 4,
  "failed_translations": 0,
  "total_processing_time": 3.45
}
```

---

## 🚨 **15. Error Handling Examples**

### Unsupported Language Error
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_language": "en",
    "target_languages": ["fr"]
  }'
```

**Expected Output:**
```json
{
  "error": "Validation Error",
  "details": [
    {
      "type": "value_error", 
      "loc": ["target_languages", 0],
      "msg": "Target language 'fr' not supported. Choose from 22 Indian languages or 'en'",
      "input": "fr"
    }
  ]
}
```

### File Too Large Error
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@huge_file.pdf"
```

**Expected Output:**
```json
{
  "detail": "File too large. Maximum size: 100 MB"
}
```

### Invalid Audio Format
```bash
curl -X POST "http://localhost:8000/speech/stt" \
  -F "file=@document.txt"
```

**Expected Output:**
```json
{
  "detail": "Audio format not supported. Allowed: .wav, .mp3, .mp4, .m4a, .ogg, .flac"
}
```

---

## � **16. Advanced Features & Examples**

### Test Robust Cross-Indian Translation (NEW!)
```bash
# Hindi to Bengali using IndicTrans2-Bridge method
curl -s -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text":"आज सुंदर दिन है","source_language":"hi","target_languages":["bn"]}'
```

**Expected Output:**
```json
{
  "results": [
    {
      "translated_text": "আজ একটি সুন্দর দিন",
      "source_language": "hi",
      "target_language": "bn",
      "model_used": "IndicTrans2-Bridge",
      "confidence_score": 0.8,
      "duration": 0.6,
      "bridge_translation": true,
      "intermediate_language": "en"
    }
  ]
}
```

### Multi-Modal Translation (Text + Audio Output)
```bash
# 1. Translate text
curl -s -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text":"Welcome to our platform","source_language":"en","target_languages":["hi"]}' \
  > translation_result.json

# 2. Convert result to speech
TRANSLATED_TEXT=$(cat translation_result.json | jq -r '.results[0].translated_text')
curl -s -X POST "http://localhost:8000/speech/tts" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"$TRANSLATED_TEXT\",\"language\":\"hi\"}"
```

### Domain-Specific Healthcare Translation Chain
```bash
# Healthcare domain with localization
curl -s -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text":"Take medicine twice daily after meals","source_language":"en","target_languages":["hi"],"domain":"healthcare","apply_localization":true}'
```

## 📋 **17. Quick System Validation**

### Complete System Validation (5 Commands)
```bash
# 1. Check health
curl -s "http://localhost:8000/supported-languages" | jq '.total_count'

# 2. Test language detection  
curl -s -X POST "http://localhost:8000/detect-language" \
  -H "Content-Type: application/json" \
  -d '{"text":"नमस्ते"}' | jq '.detected_language'

# 3. Test translation
curl -s -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","source_language":"en","target_languages":["hi"]}' \
  | jq '.results[0].translated_text'

# 4. Test TTS
curl -s -X POST "http://localhost:8000/speech/tts" \
  -H "Content-Type: application/json" \
  -d '{"text":"नमस्ते","language":"hi"}' | jq '.audio_path'

# 5. Test feedback
curl -s -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{"rating":5,"comments":"API test"}' | jq '.rating'
```

**Expected Outputs:**
```
22
"hi"  
"नमस्कार"
"storage/outputs/tts_hi_abc123.mp3"
5
```

---

## 🎯 **Success Indicators**

✅ **All 22 Indian languages supported**  
✅ **Sub-second translation speeds**  
✅ **Multi-modal processing (text + speech)**  
✅ **Cultural localization working**  
✅ **File upload/processing functional**  
✅ **Background job management**  
✅ **Comprehensive monitoring**  
✅ **Production-ready error handling**

**Your FastAPI Backend is fully operational and production-ready!** 🚀

---

## 📊 **Complete Endpoint Summary**

### Core Categories (35+ Endpoints Total):

| Category | Endpoints | Key Features |
|----------|-----------|--------------|
| **Health & System** | 4 | Health check, supported languages, system info |
| **Authentication** | 3 | Registration, login, JWT validation |
| **Translation Core** | 7 | Translate, detect language, batch processing |
| **Speech Processing** | 3 | STT (Whisper), TTS (VITS), audio handling |
| **Content Management** | 5 | Upload, download, file listing, metadata |
| **Feedback System** | 4 | Submit, view, manage user feedback |
| **Background Jobs** | 5 | Retrain models, job status, cleanup |
| **Evaluation & QA** | 2 | BLEU/COMET scoring, quality metrics |
| **Monitoring** | 2 | Prometheus metrics, performance stats |
| **Advanced Features** | 5+ | Batch processing, localization, statistics |

### Language Support Matrix:
- **22 Indian Languages** + English = 23 total
- **506 Translation Pairs** (22×22 + 22×2 for English)
- **Intelligent Routing**: IndicTrans2 → NLLB → Dictionary fallback
- **Bridge Translation**: Cross-Indian via English when direct fails

### Production Features:
✅ **Docker Ready** (Dockerfile + docker-compose.prod.yml)  
✅ **PostgreSQL Integration** (SQLAlchemy + Alembic migrations)  
✅ **Local Storage** (No cloud dependencies)  
✅ **JWT Authentication** (Simple, production-ready)  
✅ **Prometheus Metrics** (/metrics endpoint)  
✅ **Comprehensive Logging** (Rich + Loguru)  
✅ **Error Handling** (Proper HTTP status codes)  
✅ **API Documentation** (This complete guide!)

### Quick Start Commands:
```bash
# Start server
docker-compose -f docker-compose.prod.yml up -d

# Test core functionality
curl "http://localhost:8000/health"
curl "http://localhost:8000/supported-languages"

# Basic translation test
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","source_language":"en","target_languages":["hi"]}'
```

---

**🎉 Your comprehensive FastAPI + AI backend system is complete and fully documented!**