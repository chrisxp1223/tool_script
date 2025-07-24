"""Comprehensive logging system for PostCodeMon."""

import json
import logging
import logging.handlers
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
import structlog

from .config import LoggingConfig
from .errors import ConfigurationError


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from the log record
        extra_fields = {k: v for k, v in record.__dict__.items() 
                       if k not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                                   'pathname', 'filename', 'module', 'lineno', 
                                   'funcName', 'created', 'msecs', 'relativeCreated', 
                                   'thread', 'threadName', 'processName', 'process',
                                   'exc_info', 'exc_text', 'stack_info']}
        
        if extra_fields:
            log_data['extra'] = extra_fields
        
        return json.dumps(log_data, ensure_ascii=False)


class PerformanceLogger:
    """Context manager for tracking performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation}", extra={
            'operation': self.operation,
            'event': 'start',
            **self.context
        })
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation}", extra={
                'operation': self.operation,
                'event': 'complete',
                'duration_seconds': duration,
                **self.context
            })
        else:
            self.logger.error(f"Failed {self.operation}", extra={
                'operation': self.operation,
                'event': 'error',
                'duration_seconds': duration,
                'error_type': exc_type.__name__,
                'error_message': str(exc_val),
                **self.context
            })


class LogManager:
    """Central logging management for PostCodeMon."""
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        self.config = config or LoggingConfig()
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_root_logger()
        self._setup_structlog()
    
    def _setup_root_logger(self) -> None:
        """Configure the root logger with handlers and formatters."""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        if self.config.json_format:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(self.config.format))
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if self.config.file_path:
            file_path = Path(self.config.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            
            if self.config.json_format:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(self.config.format))
            
            root_logger.addHandler(file_handler)
    
    def _setup_structlog(self) -> None:
        """Configure structlog for structured logging."""
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        
        if self.config.json_format:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger instance."""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]
    
    def get_structured_logger(self, name: str) -> structlog.BoundLogger:
        """Get a structured logger instance."""
        return structlog.get_logger(name)
    
    def log_tool_execution(self, tool_name: str, command: str, 
                          return_code: int, stdout: str = "", stderr: str = "",
                          duration: float = 0.0, **context) -> None:
        """Log tool execution details."""
        logger = self.get_logger("postcodemon.execution")
        
        log_data = {
            'tool_name': tool_name,
            'command': command,
            'return_code': return_code,
            'duration_seconds': duration,
            'stdout_length': len(stdout),
            'stderr_length': len(stderr),
            **context
        }
        
        if return_code == 0:
            logger.info(f"Tool execution successful: {tool_name}", extra=log_data)
        else:
            log_data['stderr_sample'] = stderr[:500] if stderr else ""
            logger.error(f"Tool execution failed: {tool_name}", extra=log_data)
    
    def log_performance_metric(self, metric_name: str, value: Union[int, float], 
                              unit: str = "", **context) -> None:
        """Log performance metrics."""
        logger = self.get_logger("postcodemon.metrics")
        logger.info(f"Performance metric: {metric_name}", extra={
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat(),
            **context
        })
    
    def create_performance_logger(self, operation: str, **context) -> PerformanceLogger:
        """Create a performance tracking context manager."""
        logger = self.get_logger("postcodemon.performance")
        return PerformanceLogger(logger, operation, **context)
    
    def log_audit_event(self, event_type: str, user: str = "", 
                       details: Optional[Dict[str, Any]] = None, **context) -> None:
        """Log audit events for security and compliance."""
        logger = self.get_logger("postcodemon.audit")
        
        audit_data = {
            'event_type': event_type,
            'user': user or os.getenv('USER', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'details': details or {},
            **context
        }
        
        logger.info(f"Audit event: {event_type}", extra=audit_data)
    
    def update_config(self, new_config: LoggingConfig) -> None:
        """Update logging configuration at runtime."""
        self.config = new_config
        self._setup_root_logger()
        self._setup_structlog()
        
        # Clear cached loggers to pick up new configuration
        self._loggers.clear()
    
    def shutdown(self) -> None:
        """Shutdown logging system gracefully."""
        # Flush all handlers
        for logger in self._loggers.values():
            for handler in logger.handlers:
                handler.flush()
        
        # Shutdown root logger handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()
            handler.close()
        
        logging.shutdown()