# 🌐 Indian Language Localizer Backend

A **production-ready FastAPI backend system** for AI-powered multilingual translation and localization supporting **22 Indian languages**.

> ✅ **Status**: Fully operational with 100% test coverage (22/22 tests passing)

## ✨ Features

- 🔤 **Translation Engine**: IndicTrans2-based translation for 22 Indian languages
- 🗣️ **Speech-to-Text**: Whisper-powered transcription with Indian accent support
- 🔊 **Text-to-Speech**: Multi-language audio with automatic script transliteration
- 🎯 **Domain Adaptation**: Context-aware translation for healthcare, construction, education, etc.
- 🌏 **Cultural Localization**: Culturally appropriate phrase adaptation
- 📊 **Quality Metrics**: BLEU, COMET, TER, METEOR evaluation
- 🔄 **Model Retraining**: Feedback-based continuous improvement
- 🔐 **JWT Authentication**: Role-based access control (Admin, Uploader, Reviewer)
- 📦 **Local Storage**: No cloud dependencies
- 🚀 **Celery Task Queue**: Async processing with Redis
- 📈 **Prometheus Metrics**: Production monitoring
- 🐳 **Docker Ready**: Complete containerization

## 🌐 Supported Languages

The system supports **22 Indian languages**:

| Code | Language | Code | Language | Code | Language |
|------|----------|------|----------|------|----------|
| `as` | Assamese | `bn` | Bengali | `brx` | Bodo |
| `doi` | Dogri | `gu` | Gujarati | `hi` | Hindi |
| `kn` | Kannada | `ks` | Kashmiri | `kok` | Konkani |
| `mai` | Maithili | `ml` | Malayalam | `mni` | Manipuri |
| `mr` | Marathi | `ne` | Nepali | `or` | Odia |
| `pa` | Punjabi | `sa` | Sanskrit | `sat` | Santali |
| `sd` | Sindhi | `ta` | Tamil | `te` | Telugu |
| `ur` | Urdu |

## 📖 Quick Access

- **[🔗 Complete API Documentation](API_DOCUMENTATION.md)** - Full cURL examples for all endpoints
- **[🧪 Comprehensive Testing](comprehensive_api_test.py)** - 22 tests, 100% passing rate

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   FastAPI   │────▶│  PostgreSQL  │     │    Redis    │
│   Backend   │     │   Database   │     │   (Celery)  │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                         │
       │                                         ▼
       │                                  ┌─────────────┐
       │                                  │   Celery    │
       │                                  │   Workers   │
       │                                  └─────────────┘
       │                                         │
       ▼                                         ▼
┌─────────────┐                          ┌─────────────┐
│  AI Models  │                          │   Storage   │
│  - IndicTrans2                         │  - Uploads  │
│  - Whisper  │                          │  - Outputs  │
│  - TTS      │                          │  - Models   │
└─────────────┘                          └─────────────┘
```

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.104+ |
| Database | PostgreSQL 15+ |
| Cache/Queue | Redis 7+ |
| Task Queue | Celery 5.3+ |
| Translation | IndicTrans2, mBART |
| STT | OpenAI Whisper |
| TTS | Coqui TTS |
| ML Framework | PyTorch, Transformers |
| Authentication | OAuth2 + JWT |
| Monitoring | Prometheus |
| Logging | Loguru |

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd new_backend

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build and start services
docker-compose up --build

# Create initial admin user (in another terminal)
docker-compose exec backend python scripts/create_admin.py admin admin@example.com password123
```

The API will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local configuration

# Create storage directories
mkdir -p storage/uploads storage/outputs logs models data/vocabs

# Run database migrations
alembic upgrade head

# Create admin user
python scripts/create_admin.py admin admin@example.com password123

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In separate terminals, start Celery workers:
celery -A app.core.celery_app worker -Q translation --loglevel=info
celery -A app.core.celery_app worker -Q speech --loglevel=info
celery -A app.core.celery_app worker -Q evaluation,retraining --loglevel=info
```

## 📡 API Endpoints

### Authentication
- `POST /auth/register` - Register new user (admin only)
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Content Management
- `POST /content/upload` - Upload file for translation
- `GET /content/files` - List uploaded files
- `GET /content/files/{id}` - Get file details
- `DELETE /content/files/{id}` - Delete file

### Translation
- `GET /supported-languages` - List supported languages
- `POST /detect-language` - Auto-detect language
- `POST /translate` - Translate text/file
- `POST /localize/context` - Apply domain localization

### Speech Processing
- `POST /speech/stt` - Speech-to-text conversion
- `POST /speech/tts` - Text-to-speech synthesis

### Feedback & Evaluation
- `POST /feedback` - Submit feedback
- `GET /feedback` - List feedback
- `POST /evaluate/run` - Evaluate translation quality
- `GET /evaluate/results` - Get evaluation results

### Model Management
- `POST /retrain/trigger` - Trigger model retraining (admin)
- `GET /jobs/{id}` - Check job status

### Monitoring
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## 🔑 Authentication

All API endpoints (except `/health`, `/metrics`, `/supported-languages`) require JWT authentication.

### Login Flow

```bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}

# 2. Use token in subsequent requests
curl -X POST "http://localhost:8000/translate" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "source_language": "en", "target_languages": ["hi"]}'
```

## 💡 Usage Examples

### Translate Text

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "admin", "password": "password123"}
)
token = response.json()["access_token"]

# Translate
headers = {"Authorization": f"Bearer {token}"}
translation_request = {
    "text": "Welcome to our platform",
    "source_language": "en",
    "target_languages": ["hi", "ta", "bn"],
    "domain": "healthcare",
    "apply_localization": True
}

response = requests.post(
    "http://localhost:8000/translate",
    json=translation_request,
    headers=headers
)

job_id = response.json()["id"]

# Check job status
status_response = requests.get(
    f"http://localhost:8000/jobs/{job_id}",
    headers=headers
)
print(status_response.json())
```

### Speech-to-Text

```python
with open("audio.mp3", "rb") as audio_file:
    files = {"file": audio_file}
    response = requests.post(
        "http://localhost:8000/speech/stt",
        files=files,
        headers=headers
    )
    job_id = response.json()["id"]
```

### Text-to-Speech

```python
tts_request = {
    "text": "नमस्ते, आपका स्वागत है",
    "language": "hi",
    "voice": "default",
    "speed": 1.0
}

response = requests.post(
    "http://localhost:8000/speech/tts",
    json=tts_request,
    headers=headers
)
```

## 📊 Database Schema

- **users** - User accounts with role-based access
- **files** - Uploaded content files
- **jobs** - Background task tracking
- **translations** - Translation outputs
- **feedback** - User feedback and corrections
- **evaluations** - Quality metrics (BLEU, COMET, etc.)

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-secret-key
JWT_EXPIRATION=3600

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage
STORAGE_DIR=/app/storage
UPLOAD_DIR=/app/storage/uploads
OUTPUT_DIR=/app/storage/outputs

# Environment
ENVIRONMENT=production
DEBUG=false
```

## 📈 Monitoring

Access Prometheus metrics at: **http://localhost:8000/metrics**

Key metrics:
- `translation_requests_total` - Total translation requests
- `translation_duration_seconds` - Translation processing time
- `bleu_score_average` - Average BLEU scores
- `active_jobs` - Current active jobs
- `job_failures_total` - Failed jobs count

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📝 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🐛 Troubleshooting

### Models Not Loading

If AI models fail to load:
```bash
# Manually download models
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ai4bharat/IndicTrans2-en-indic-1B')"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

### Celery Workers Not Processing

```bash
# Check Redis connection
docker-compose logs redis

# Restart workers
docker-compose restart celery_translation celery_speech
```

## 🔒 Security

- JWT-based authentication with configurable expiration
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM
- CORS configuration for API security

## 🚀 Production Deployment

### On DigitalOcean/VPS

```bash
# 1. Clone repository
git clone <repo> && cd new_backend

# 2. Configure environment
cp .env.example .env
nano .env  # Update with production values

# 3. Start services
docker-compose up -d

# 4. Create admin
docker-compose exec backend python scripts/create_admin.py admin admin@example.com <secure-password>

# 5. Enable on boot
sudo systemctl enable docker
```

### Environment Variables for Production

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-secure-key>
DATABASE_URL=postgresql://...
```

## 📚 Documentation

### API Documentation
- **[Complete API Guide](API_DOCUMENTATION.md)** - Frontend developer guide with cURL examples
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

### Testing
- **[Comprehensive Test Suite](comprehensive_api_test.py)** - 22 tests covering all endpoints (100% passing)
- **[Quick Test Runner](quick_api_test.py)** - Essential functionality tests

```bash
# Run quick tests
python quick_api_test.py

# Run comprehensive tests
python comprehensive_api_test.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- **AI4Bharat** for IndicTrans2 models
- **OpenAI** for Whisper
- **Coqui** for TTS models
- **FastAPI** community

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@example.com

---

**Built with ❤️ for Indian language localization**

