# 📁 PROJECT STRUCTURE GUIDE

## 🎯 Understanding the Codebase

This document explains the **clean, organized structure** of the Indian Language Localizer Backend after cleanup.

---

## 🏗️ **Core Application Structure**

### 📱 **`app/main.py`** - Application Entry Point
```python
# Main FastAPI application with lifespan management
# Handles startup/shutdown, CORS, middleware, and route registration
```

### ⚙️ **`app/core/`** - Configuration & Database
```python
app/core/
├── config.py      # Environment configuration & settings
├── db.py         # Database connection & session management  
└── security.py   # JWT authentication & password utilities
```

### 🌐 **`app/routes/`** - API Endpoints
```python
app/routes/
├── auth.py         # POST /auth/login, /auth/register
├── translation.py  # POST /translate, GET /supported-languages
├── speech.py       # POST /speech/stt, /speech/tts
├── content.py      # POST /content/upload, GET /content/files
├── feedback.py     # POST /feedback, GET /feedback/stats
├── evaluation.py   # POST /evaluate/run, GET /evaluate/results
└── jobs.py         # Background job management
```

### 🧠 **`app/services/`** - Business Logic
```python
app/services/
├── nlp_engine.py      # 🔤 Core translation engine (IndicTrans2, NLLB)
├── speech_engine.py   # 🗣️ Speech processing (Whisper STT, TTS)
├── localization.py    # 🌍 Cultural adaptation & domain vocabularies
├── retrain_manager.py # 🔄 Model retraining orchestration
└── direct_retrain.py  # 🎯 Direct model fine-tuning
```

### 📊 **`app/models/`** - Database Models
```python
app/models/
├── user.py        # User accounts & authentication
├── file.py        # File upload & management
├── translation.py # Translation history & results
├── feedback.py    # User feedback & ratings
└── evaluation.py  # Model performance metrics
```

### 📋 **`app/schemas/`** - API Schemas
```python
app/schemas/
├── user.py        # User registration, login requests
├── translation.py # Translation requests & responses
├── speech.py      # STT/TTS API schemas
├── file.py        # File upload schemas
├── feedback.py    # Feedback submission schemas
└── evaluation.py  # Evaluation result schemas
```

### 🛠️ **`app/utils/`** - Utilities
```python
app/utils/
├── logger.py        # 📝 Structured logging with context
├── file_manager.py  # 📁 File operations & storage management
├── metrics.py       # 📊 Prometheus metrics collection
├── performance.py   # ⚡ Performance optimization & monitoring
└── text_extractor.py # 📄 Text extraction from various formats
```

---

## 📚 **Data & Configuration**

### **`data/vocabs/`** - Domain Vocabularies
```json
data/vocabs/
├── general.json      # Common phrases & terms
├── healthcare.json   # Medical terminology
└── construction.json # Construction industry terms
```

### **`scripts/`** - Utility Scripts
```python
scripts/
├── download_models.py # Download AI models (IndicTrans2, NLLB, Whisper)
├── create_admin.py   # Create admin user account
└── reset_admin.py    # Reset admin credentials
```

### **`alembic/`** - Database Migrations
```
alembic/
├── versions/         # Migration files
├── env.py           # Migration environment
└── script.py.mako   # Migration template
```

---

## 🔄 **How Everything Works Together**

### 1. **Request Flow**
```
User Request → routes/ → services/ → models/ → Database
                    ↓
               utils/ (logging, metrics)
```

### 2. **Translation Process**
```
routes/translation.py 
    → services/nlp_engine.py (IndicTrans2/NLLB)
    → services/localization.py (cultural adaptation)
    → models/translation.py (save results)
```

### 3. **Speech Processing**
```
routes/speech.py
    → services/speech_engine.py (Whisper STT/TTS)
    → utils/file_manager.py (audio handling)
    → storage/ (file storage)
```

### 4. **User Management**
```
routes/auth.py
    → core/security.py (JWT tokens)
    → models/user.py (user data)
    → core/db.py (database sessions)
```

---

## 🎯 **Key Design Principles**

### ✅ **Separation of Concerns**
- **Routes**: Handle HTTP requests/responses only
- **Services**: Contain all business logic
- **Models**: Define data structure & relationships
- **Utils**: Provide reusable functionality

### ✅ **Single Responsibility**
- Each file has one clear purpose
- Services are focused on specific domains
- Utils are atomic and composable

### ✅ **Dependency Injection**
- Configuration through environment variables
- Service dependencies injected via FastAPI
- Database sessions managed centrally

### ✅ **Error Handling**
- Centralized logging in utils/logger.py
- Consistent error responses from routes
- Graceful fallbacks in services

---

## 🚀 **Adding New Features**

### **1. New API Endpoint**
```python
# 1. Add route in app/routes/
# 2. Add schema in app/schemas/
# 3. Add business logic in app/services/
# 4. Add database model if needed in app/models/
# 5. Register route in app/main.py
```

### **2. New AI Model**
```python
# 1. Add model loading logic to services/nlp_engine.py
# 2. Update download script in scripts/download_models.py
# 3. Add configuration in app/core/config.py
# 4. Update API schemas if needed
```

### **3. New Domain Vocabulary**
```python
# 1. Create JSON file in data/vocabs/
# 2. Update services/localization.py to load it
# 3. Add domain to configuration
```

---

## 📝 **File Naming Conventions**

### ✅ **Consistent Patterns**
- **Routes**: Verb-focused (auth.py, translation.py)
- **Services**: Domain-focused (nlp_engine.py, speech_engine.py)
- **Models**: Entity-focused (user.py, file.py)
- **Utils**: Function-focused (logger.py, metrics.py)

### ✅ **Clear Dependencies**
- Core modules have no dependencies on other app modules
- Services can depend on models and utils
- Routes depend on services, models, and schemas
- Utils are dependency-free

---

## 🎊 **Clean Architecture Benefits**

✅ **Easy to Understand** - Clear separation and naming
✅ **Easy to Test** - Each component is isolated
✅ **Easy to Extend** - Add features without breaking existing code
✅ **Easy to Maintain** - Find and fix issues quickly
✅ **Production Ready** - Robust error handling and monitoring

---

This structure ensures that **everyone can understand how things work** and easily contribute to the project!