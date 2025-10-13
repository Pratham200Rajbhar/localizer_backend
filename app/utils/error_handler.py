
"""
Robust Error Handler for Production System
"""
import logging
import traceback
from functools import wraps
from fastapi import HTTPException, status
from typing import Callable, Any

app_logger = logging.getLogger(__name__)

def robust_endpoint(endpoint_name: str):
    """Decorator for robust error handling in endpoints"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except ValueError as e:
                app_logger.error(f"{endpoint_name} validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation error in {endpoint_name}: {str(e)}"
                )
            except FileNotFoundError as e:
                app_logger.error(f"{endpoint_name} file not found: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resource not found in {endpoint_name}: {str(e)}"
                )
            except MemoryError as e:
                app_logger.error(f"{endpoint_name} memory error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail=f"Insufficient memory for {endpoint_name}"
                )
            except TimeoutError as e:
                app_logger.error(f"{endpoint_name} timeout: {e}")
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail=f"Request timeout in {endpoint_name}"
                )
            except Exception as e:
                app_logger.error(f"{endpoint_name} unexpected error: {e}")
                app_logger.error(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Internal error in {endpoint_name}: {str(e)}"
                )
        return wrapper
    return decorator

def safe_model_operation(operation_name: str):
    """Decorator for safe model operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except RuntimeError as e:
                app_logger.error(f"{operation_name} runtime error: {e}")
                if "CUDA" in str(e) or "GPU" in str(e):
                    app_logger.warning(f"GPU error in {operation_name}, falling back to CPU")
                    # Could implement CPU fallback here
                raise
            except Exception as e:
                app_logger.error(f"{operation_name} error: {e}")
                app_logger.error(f"Traceback: {traceback.format_exc()}")
                raise
        return wrapper
    return decorator
