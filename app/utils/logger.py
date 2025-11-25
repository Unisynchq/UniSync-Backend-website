"""
Structured logging utility
"""
import os
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import json


class StructuredLogger:
    """Production-ready structured logger"""
    
    def __init__(self, name: str = "unisync"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.correlation_id: Optional[str] = None
        self.is_development = os.getenv("ENVIRONMENT", "development") == "development"
        
        # Configure handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._get_formatter())
            self.logger.addHandler(handler)
    
    def _get_formatter(self):
        """Get appropriate formatter based on environment"""
        if self.is_development:
            return logging.Formatter(
                '[%(asctime)s] [%(correlation_id)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # JSON formatter for production
            return JSONFormatter()
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request tracking"""
        self.correlation_id = correlation_id
    
    def _log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Internal logging method"""
        extra = {
            'correlation_id': self.correlation_id or 'unknown',
            **(context or {})
        }
        
        if self.is_development:
            context_str = json.dumps(context, indent=2) if context else ""
            log_message = f"{message} {context_str}".strip()
            getattr(self.logger, level.lower())(log_message, extra=extra)
        else:
            # Structured JSON logging for production
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': level.upper(),
                'correlation_id': self.correlation_id,
                'message': message,
                **(context or {})
            }
            self.logger.log(getattr(logging, level.upper()), json.dumps(log_data), extra=extra)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log('INFO', message, context)
    
    def warn(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log('WARNING', message, context)
    
    def error(self, message: str, error: Optional[Exception] = None, context: Optional[Dict[str, Any]] = None):
        """Log error message"""
        error_context = context or {}
        if error:
            error_context['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': self._get_traceback(error) if hasattr(error, '__traceback__') else None
            }
        self._log('ERROR', message, error_context)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log debug message (only in development)"""
        if self.is_development:
            self._log('DEBUG', message, context)
    
    def _get_traceback(self, error: Exception) -> Optional[str]:
        """Extract traceback as string"""
        import traceback
        if error.__traceback__:
            return ''.join(traceback.format_tb(error.__traceback__))
        return None


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'correlation_id': getattr(record, 'correlation_id', 'unknown'),
            'message': record.getMessage(),
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
                          'pathname', 'process', 'processName', 'relativeCreated', 'thread',
                          'threadName', 'exc_info', 'exc_text', 'stack_info', 'correlation_id']:
                log_data[key] = value
        
        return json.dumps(log_data)


# Global logger instance
logger = StructuredLogger()

