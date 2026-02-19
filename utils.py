"""
Production Utilities and Helpers
Common utilities for error handling, validation, response formatting
"""

import logging
import functools
import time
from flask import jsonify
from datetime import datetime
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
        """Return a successful response"""
        response = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(error: str, status_code: int = 400, details: Dict = None) -> tuple:
        """Return an error response"""
        response = {
            'success': False,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(field: str, message: str) -> tuple:
        """Return a validation error response"""
        response = {
            'success': False,
            'error': 'Validation failed',
            'timestamp': datetime.now().isoformat(),
            'details': {'field': field, 'message': message}
        }
        return jsonify(response), 422
    
    @staticmethod
    def not_found(resource: str = "Resource") -> tuple:
        """Return a not found response"""
        return APIResponse.error(f"{resource} not found", 404)


class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_node_id(node_id: str) -> bool:
        """Validate node ID format"""
        if not node_id or not isinstance(node_id, str):
            return False
        return len(node_id) <= 255 and len(node_id) > 0
    
    @staticmethod
    def is_valid_percentage(value: float) -> bool:
        """Validate percentage value (0-100)"""
        try:
            val = float(value)
            return 0 <= val <= 100
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def is_valid_metric(value: float, min_val: float = 0, max_val: float = 100) -> bool:
        """Validate metric value within range"""
        try:
            val = float(value)
            return min_val <= val <= max_val
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)[:max_length]
        return value.strip()[:max_length]


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    @staticmethod
    def timer(func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            if elapsed_time > 1.0:  # Log slow operations
                logger.warning(f"Slow operation: {func.__name__} took {elapsed_time:.2f}s")
            else:
                logger.debug(f"{func.__name__} took {elapsed_time:.3f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get current memory usage statistics"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }


class ErrorHandler:
    """Central error handling utilities"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> tuple:
        """Handle and log errors uniformly"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        logger.error(f"Error in {context}: {error_type}: {error_msg}", exc_info=True)
        
        # Map common errors to HTTP status codes
        error_handlers = {
            'ValueError': 400,
            'KeyError': 404,
            'TypeError': 400,
            'TimeoutError': 504,
            'ConnectionError': 503,
        }
        
        status_code = error_handlers.get(error_type, 500)
        return APIResponse.error(f"{error_type}: {error_msg}", status_code)
    
    @staticmethod
    def handle_timeout(func: Callable, timeout: int = 30) -> Callable:
        """Decorator to handle function timeouts"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Timeout or error in {func.__name__}: {e}", exc_info=True)
                raise
        return wrapper


class DataCache:
    """Simple in-memory cache for frequently accessed data"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache"""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Store in cache"""
        if len(self.cache) >= self.max_size:
            # Remove least accessed item
            least_accessed = min(self.access_count, key=self.access_count.get)
            del self.cache[least_accessed]
            del self.access_count[least_accessed]
        
        self.cache[key] = value
        self.access_count[key] = 1
    
    def clear(self) -> None:
        """Clear the cache"""
        self.cache.clear()
        self.access_count.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)


class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit for identifier"""
        if identifier in self.requests:
            del self.requests[identifier]


# Global instances
response_handler = APIResponse()
input_validator = InputValidator()
error_handler = ErrorHandler()
cache = DataCache()
rate_limiter = RateLimiter()
