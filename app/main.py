"""
Main FastAPI application
Indian Language Localizer Backend
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
from app.core.config import get_settings
from app.core.db import init_db
from app.utils.logger import app_logger
from app.utils.metrics import get_metrics
from app.utils.performance import perf_monitor, cleanup_resources
from app.routes import auth, content, translation, speech, feedback

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    app_logger.info("Starting Indian Language Localizer Backend...")
    
    # Initialize database
    try:
        init_db()
        app_logger.info("Database initialized")
    except Exception as e:
        app_logger.error(f"Database initialization error: {e}")
    
    # Create storage directories
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/vocabs", exist_ok=True)
    app_logger.info("Storage directories created")
    
    # Pre-load models (optional, can be lazy-loaded)
    # from app.services.nlp_engine import nlp_engine
    # nlp_engine.load_model("IndicTrans2-en-indic", "en-indic")
    
    app_logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down application...")
    cleanup_resources()
    app_logger.info("Resources cleaned up")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Multilingual Translation & Localization for 22 Indian Languages",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Performance monitoring middleware
@app.middleware("http")
async def performance_monitoring_middleware(request: Request, call_next):
    """Performance monitoring and request timing middleware"""
    start_time = time.time()
    perf_monitor.start_request()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add timing headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(id(request))
        
        # Record metrics
        perf_monitor.end_request(process_time)
        
        return response
    except Exception as e:
        perf_monitor.end_request()
        raise e


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    app_logger.warning(f"Validation error: {exc}")
    
    # Convert errors to JSON-serializable format
    serializable_errors = []
    for error in exc.errors():
        serializable_error = {
            "type": error.get("type", "unknown"),
            "loc": error.get("loc", []),
            "msg": str(error.get("msg", "Validation error")),
            "input": str(error.get("input", ""))
        }
        serializable_errors.append(serializable_error)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": serializable_errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    app_logger.error("Unexpected error: {}", str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/health/db", tags=["Health"])
async def health_check_db():
    """Database health check"""
    try:
        from app.core.db import get_db
        from sqlalchemy import text
        
        # Test database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@app.get("/health/detailed", tags=["Health"])
async def health_check_detailed():
    """Detailed health check"""
    try:
        from app.core.db import get_db
        from sqlalchemy import text
        import psutil
        
        # Test database connection
        db_status = "unknown"
        try:
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db.close()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Get system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "timestamp": time.time(),
            "database": db_status,
            "system": {
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%",
                "cpu_count": psutil.cpu_count()
            },
            "services": {
                "translation": "available",
                "speech": "available",
                "file_upload": "available"
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics"""
    return get_metrics()


# Performance metrics endpoint
@app.get("/performance", tags=["Monitoring"])
async def performance_metrics():
    """Get current performance metrics"""
    return {
        "status": "ok",
        "metrics": perf_monitor.get_metrics(),
        "memory": perf_monitor.get_memory_info(),
        "system": perf_monitor.get_system_info()
    }


# Include routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(content.upload_router)  # Add simple upload router
app.include_router(translation.router)
app.include_router(speech.router)
app.include_router(feedback.router)
app.include_router(feedback.simple_router)  # Add simple feedback router

# Add missing evaluation router (commented due to dependency conflicts)
# from app.routes import evaluation
# app.include_router(evaluation.router)

# Add jobs/background task router
from app.routes import jobs
app.include_router(jobs.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

