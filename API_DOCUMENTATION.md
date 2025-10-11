# 🌐 Indian Language Localizer API Documentation

## 🚀 **Complete Frontend Developer Guide**

This document provides all the API endpoints with cURL examples for the Indian Language Localizer Backend. The system supports **22 Indian languages** plus English with translation, speech processing, and evaluation capabilities.

---

## 🔐 **Authentication**

All API endpoints require JWT authentication except `/health` and `/supported-languages`.

### Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Register New User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

---

## 🌍 **Core Language & Translation APIs**

### Health Check
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Get Supported Languages
```bash
curl -X GET "http://127.0.0.1:8000/supported-languages" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "as": "Assamese",
  "bn": "Bengali", 
  "gu": "Gujarati",
  "hi": "Hindi",
  "kn": "Kannada",
  "ml": "Malayalam",
  "mr": "Marathi",
  "or": "Odia",
  "pa": "Punjabi",
  "ta": "Tamil",
  "te": "Telugu",
  "ur": "Urdu"
  // ... and 10 more languages
}
```

### Language Detection
```bash
curl -X POST "http://127.0.0.1:8000/detect-language" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "नमस्ते दुनिया"
  }'
```

**Response:**
```json
{
  "detected_language": "hi",
  "language_name": "Hindi",
  "confidence": 0.95
}
```

### Text Translation
```bash
curl -X POST "http://127.0.0.1:8000/translate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_language": "en",
    "target_languages": ["hi", "ta", "bn"],
    "domain": "general",
    "apply_localization": true
  }'
```

**Response:**
```json
{
  "results": [
    {
      "translated_text": "हैलो वर्ल्ड",
      "source_language": "en",
      "target_language": "hi",
      "source_language_name": "English",
      "target_language_name": "Hindi",
      "model_used": "IndicTrans2-en-indic",
      "confidence_score": 0.9,
      "duration": 0.34,
      "domain": "general",
      "translation_id": 123
    }
  ],
  "total_translations": 3,
  "total_duration": 1.04
}
```

---

## 🎤 **Speech Processing APIs**

### Speech-to-Text (STT)
```bash
curl -X POST "http://127.0.0.1:8000/speech/stt" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@audio_sample.mp3"
```

**Response:**
```json
{
  "transcript": "नमस्ते, यह एक परीक्षण है",
  "language_detected": "hi",
  "language_name": "Hindi",
  "confidence": 0.95,
  "duration": 2.45,
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "नमस्ते, यह एक परीक्षण है"
    }
  ],
  "model_used": "whisper-large-v3"
}
```

### Text-to-Speech (TTS) ✨ FIXED
Generate audio from text in 22 Indian languages with automatic transliteration.

```bash
curl -X POST "http://127.0.0.1:8000/speech/tts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "नमस्ते दुनिया",
    "language": "hi"
  }'
```

**Features:**
- ✅ Automatic transliteration for Indian scripts
- ✅ Phonetic approximation for better pronunciation  
- ✅ Robust fallback mechanisms
- ✅ Support for all 22 Indian languages

**Response:**
```json
{
  "audio_path": "./storage/outputs/tts_hi_abc123.wav",
  "language": "hi",
  "language_name": "Hindi",
  "duration": 2.1,
  "generation_time": 1.8,
  "format": "wav"
}
```

---

## 📊 **Evaluation & Quality APIs**

### Run Translation Evaluation
```bash
curl -X POST "http://127.0.0.1:8000/evaluate/run" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "translation_id": 123,
    "reference_text": "नमस्ते संसार"
  }'
```

**Response:**
```json
{
  "id": 45,
  "translation_id": 123,
  "bleu_score": 0.85,
  "comet_score": 0.78,
  "reference_text": "नमस्ते संसार",
  "evaluator_id": 1,
  "created_at": "2025-10-12T10:30:00Z"
}
```

---

## 💬 **Feedback System APIs**

### Submit Feedback
```bash
curl -X POST "http://127.0.0.1:8000/feedback" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "translation_id": 123,
    "rating": 4,
    "comments": "Good translation, minor context issues",
    "corrections": {
      "suggested_text": "नमस्कार संसार"
    }
  }'
```

**Response:**
```json
{
  "id": 67,
  "translation_id": 123,
  "user_id": 1,
  "rating": 4,
  "comments": "Good translation, minor context issues",
  "corrections": "{\"suggested_text\": \"नमस्कार संसार\"}",
  "created_at": "2025-10-12T10:35:00Z"
}
```

### Get All Feedback
```bash
curl -X GET "http://127.0.0.1:8000/feedback" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 67,
    "translation_id": 123,
    "user_id": 1,
    "rating": 4,
    "comments": "Good translation",
    "corrections": null,
    "created_at": "2025-10-12T10:35:00Z"
  }
]
```

---

## 📁 **File Management APIs**

### Upload File
```bash
curl -X POST "http://127.0.0.1:8000/content/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "domain=healthcare" \
  -F "source_language=en"
```

**Response:**
```json
{
  "id": 89,
  "filename": "document_abc123.pdf",
  "original_filename": "document.pdf",
  "path": "./storage/uploads/user123/document_abc123.pdf",
  "file_type": "application/pdf",
  "size": 245760,
  "domain": "healthcare",
  "source_language": "en",
  "uploader_id": 1,
  "created_at": "2025-10-12T10:40:00Z"
}
```

### Get User Files
```bash
curl -X GET "http://127.0.0.1:8000/content/files" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Translate File Content
```bash
curl -X POST "http://127.0.0.1:8000/translate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 89,
    "source_language": "en",
    "target_languages": ["hi", "ta"]
  }'
```

---

## ⚙️ **Error Handling**

### Common HTTP Status Codes

- **200 OK** - Success
- **400 Bad Request** - Invalid input/validation error
- **401 Unauthorized** - Missing or invalid token
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation failed
- **500 Internal Server Error** - Server error

### Error Response Format
```json
{
  "error": "Validation Error",
  "details": [
    {
      "type": "value_error",
      "loc": ["body", "source_language"],
      "msg": "Source language 'xyz' not supported",
      "input": "xyz"
    }
  ]
}
```

---

## 🔧 **Integration Examples**

### JavaScript/React Example
```javascript
// Authentication
const loginResponse = await fetch('http://127.0.0.1:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=admin&password=admin123'
});
const { access_token } = await loginResponse.json();

// Translation
const translationResponse = await fetch('http://127.0.0.1:8000/translate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: "Hello world",
    source_language: "en",
    target_languages: ["hi"]
  })
});
const translationData = await translationResponse.json();
```

### Python Example
```python
import requests

# Login
login_response = requests.post(
    'http://127.0.0.1:8000/auth/login',
    data={'username': 'admin', 'password': 'admin123'}
)
token = login_response.json()['access_token']

# Translation
headers = {'Authorization': f'Bearer {token}'}
translation_response = requests.post(
    'http://127.0.0.1:8000/translate',
    json={
        'text': 'Hello world',
        'source_language': 'en',
        'target_languages': ['hi']
    },
    headers=headers
)
result = translation_response.json()
```

---

## 🌟 **Supported Languages List**

| Code | Language | Script |
|------|----------|---------|
| as | Assamese | Bengali |
| bn | Bengali | Bengali |
| brx | Bodo | Devanagari |
| doi | Dogri | Devanagari |
| gu | Gujarati | Gujarati |
| hi | Hindi | Devanagari |
| kn | Kannada | Kannada |
| ks | Kashmiri | Devanagari |
| gom | Konkani | Devanagari |
| mai | Maithili | Devanagari |
| ml | Malayalam | Malayalam |
| mni | Manipuri | Bengali |
| mr | Marathi | Devanagari |
| ne | Nepali | Devanagari |
| or | Odia | Odia |
| pa | Punjabi | Gurmukhi |
| sa | Sanskrit | Devanagari |
| sat | Santali | Devanagari |
| sd | Sindhi | Devanagari |
| ta | Tamil | Tamil |
| te | Telugu | Telugu |
| ur | Urdu | Arabic |

---

## 📋 **Rate Limits & Performance**

- **Translation**: ~3-5 seconds per request
- **STT**: ~15-30 seconds depending on audio length
- **TTS**: ~1-3 seconds per request
- **File Upload**: Max 50MB per file
- **Concurrent Requests**: Recommended max 10 per minute

---

## 🛠️ **Development Notes**

1. **Base URL**: Change `127.0.0.1:8000` to your production domain
2. **Authentication**: Tokens expire after 24 hours
3. **File Paths**: Audio files are served from `/storage/outputs/`
4. **Models**: Uses IndicTrans2, Whisper, and YourTTS
5. **Database**: PostgreSQL with full ACID compliance

---

*Last updated: October 12, 2025*
*API Version: 1.0.0*