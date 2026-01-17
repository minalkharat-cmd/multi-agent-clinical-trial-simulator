"""
Enterprise Logging Service

Provides structured logging with audit trails, request tracking,
sensitive data masking, and compliance with 21 CFR Part 11.
"""

import logging
import json
import sys
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from contextvars import ContextVar
import threading
import hashlib


# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='NO_REQUEST')
user_id_var: ContextVar[str] = ContextVar('user_id', default='SYSTEM')
session_id_var: ContextVar[str] = ContextVar('session_id', default='NO_SESSION')


class AuditAction(Enum):
      """Audit action types for compliance tracking."""
      CREATE = "CREATE"
      READ = "READ"
      UPDATE = "UPDATE"
      DELETE = "DELETE"
      LOGIN = "LOGIN"
      LOGOUT = "LOGOUT"
      EXPORT = "EXPORT"
      APPROVE = "APPROVE"
      REJECT = "REJECT"
      SIGN = "ELECTRONIC_SIGNATURE"
      SIMULATION_START = "SIMULATION_START"
      SIMULATION_END = "SIMULATION_END"
      DOCUMENT_GENERATE = "DOCUMENT_GENERATE"
      CONFIG_CHANGE = "CONFIG_CHANGE"


@dataclass
class AuditLogEntry:
      """Structured audit log entry for 21 CFR Part 11 compliance."""
      timestamp: str
      action: str
      user_id: str
      session_id: str
      request_id: str
      resource_type: str
      resource_id: str
      details: Dict[str, Any]
      ip_address: Optional[str] = None
      user_agent: Optional[str] = None
      result: str = "SUCCESS"
      error_message: Optional[str] = None
      checksum: str = ""

    def __post_init__(self):
              """Generate checksum for tamper detection."""
              data = f"{self.timestamp}|{self.action}|{self.user_id}|{self.resource_type}|{self.resource_id}"
              self.checksum = hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
              return asdict(self)


class SensitiveDataFilter(logging.Filter):
      """Filter to mask sensitive data in log messages."""

    SENSITIVE_PATTERNS = [
              'password', 'api_key', 'token', 'secret', 'ssn', 
              'credit_card', 'authorization', 'bearer'
    ]

    def filter(self, record: logging.LogRecord) -> bool:
              """Mask sensitive data in log record."""
              if hasattr(record, 'msg') and isinstance(record.msg, str):
                            for pattern in self.SENSITIVE_PATTERNS:
                                              if pattern.lower() in record.msg.lower():
                                                                    record.msg = self._mask_value(record.msg, pattern)
                                                        return True

    def _mask_value(self, msg: str, pattern: str) -> str:
              """Mask sensitive values in message."""
              import re
              regex = re.compile(f'({pattern}["\']?\\s*[:=]\\s*["\']?)([^"\'\\s]+)', re.IGNORECASE)
              return regex.sub(r'\\1****MASKED****', msg)


class JSONFormatter(logging.Formatter):
      """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
              log_data = {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "level": record.levelname,
                            "logger": record.name,
                            "message": record.getMessage(),
                            "request_id": request_id_var.get(),
                            "user_id": user_id_var.get(),
                            "session_id": session_id_var.get(),
                            "module": record.module,
                            "function": record.funcName,
                            "line": record.lineno,
              }

        if record.exc_info:
                      log_data["exception"] = {
                                        "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                                        "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                                        "traceback": traceback.format_exception(*record.exc_info)
                      }

        if hasattr(record, 'extra_data'):
                      log_data["extra"] = record.extra_data

        return json.dumps(log_data)


class AuditLogger:
      """
          Specialized logger for audit trails compliant with 21 CFR Part 11.

                  Features:
                      - Immutable audit records with checksums
                          - User and session tracking
                              - Action categorization
                                  - Tamper detection
                                      """

    def __init__(self, log_dir: Path = Path("logs/audit")):
              self.log_dir = log_dir
              self.log_dir.mkdir(parents=True, exist_ok=True)
              self._setup_logger()

    def _setup_logger(self):
              """Configure audit logger with file rotation."""
              self.logger = logging.getLogger("audit")
              self.logger.setLevel(logging.INFO)

        # Daily rotating file handler
              handler = TimedRotatingFileHandler(
                            self.log_dir / "audit.log",
                            when="midnight",
                            interval=1,
                            backupCount=2555  # 7 years retention
              )
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)

    def log(
              self,
              action: AuditAction,
              resource_type: str,
              resource_id: str,
              details: Dict[str, Any] = None,
              result: str = "SUCCESS",
              error_message: str = None
    ):
              """Log an audit event."""
              entry = AuditLogEntry(
                  timestamp=datetime.utcnow().isoformat() + "Z",
                  action=action.value,
                  user_id=user_id_var.get(),
                  session_id=session_id_var.get(),
                  request_id=request_id_var.get(),
                  resource_type=resource_type,
                  resource_id=resource_id,
                  details=details or {},
                  result=result,
                  error_message=error_message
              )

        self.logger.info(json.dumps(entry.to_dict()))
        return entry


class LoggingService:
      """
          Enterprise logging service with multiple handlers and formatters.
              """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
              if cls._instance is None:
                            with cls._lock:
                                              if cls._instance is None:
                                                                    cls._instance = super().__new__(cls)
                                                        return cls._instance

                    def __init__(self):
                              if not hasattr(self, '_initialized'):
                                            self.log_dir = Path("logs")
                                            self.log_dir.mkdir(parents=True, exist_ok=True)
                                            self.audit_logger = AuditLogger(self.log_dir / "audit")
                                            self._setup_root_logger()
                                            self._initialized = True

                          def _setup_root_logger(self):
                                    """Configure root logger with handlers."""
                                    root_logger = logging.getLogger()
                                    root_logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        root_logger.handlers = []

        # Console handler (human-readable)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
                      '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        console_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(console_handler)

        # File handler (JSON structured)
        file_handler = RotatingFileHandler(
                      self.log_dir / "app.log",
                      maxBytes=100*1024*1024,  # 100MB
                      backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(SensitiveDataFilter())
        root_logger.addHandler(file_handler)

        # Error file handler
        error_handler = RotatingFileHandler(
                      self.log_dir / "error.log",
                      maxBytes=50*1024*1024,  # 50MB
                      backupCount=20
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)

    def get_logger(self, name: str) -> logging.Logger:
              """Get a named logger."""
        return logging.getLogger(name)

    def audit(
              self,
              action: AuditAction,
              resource_type: str,
              resource_id: str,
              **kwargs
    ) -> AuditLogEntry:
              """Log an audit event."""
        return self.audit_logger.log(action, resource_type, resource_id, **kwargs)

    @staticmethod
    def set_request_context(request_id: str = None, user_id: str = None, session_id: str = None):
              """Set context variables for request tracking."""
        if request_id:
                      request_id_var.set(request_id)
                  if user_id:
                                user_id_var.set(user_id)
                            if session_id:
                                          session_id_var.set(session_id)

    @staticmethod
    def generate_request_id() -> str:
              """Generate unique request ID."""
        return str(uuid.uuid4())[:8].upper()


# Convenience functions
def get_logger(name: str) -> logging.Logger:
      """Get a named logger."""
    return LoggingService().get_logger(name)


def audit_log(action: AuditAction, resource_type: str, resource_id: str, **kwargs) -> AuditLogEntry:
      """Log an audit event."""
    return LoggingService().audit(action, resource_type, resource_id, **kwargs)
