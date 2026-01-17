"""
ClinicalMind API Module

This module provides the RESTful API interface for the Clinical Trial Simulator.
Built with FastAPI for high performance and automatic OpenAPI documentation.

Endpoints:
---------
- /health: Health check endpoint
- /api/v1/simulations: Clinical trial simulation management
- /api/v1/patients: Patient population endpoints
- /api/v1/drugs: Drug interaction analysis
- /api/v1/adverse-events: Adverse event prediction
- /api/v1/dosing: Dosing optimization
- /api/v1/regulatory: FDA document generation
"""

from .main import app, create_app
from .routes import router
from .middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
)
from .dependencies import (
    get_db,
    get_redis,
    get_current_user,
    get_gemini_client,
)

__all__ = [
      # Application
    "app",
      "create_app",
      "router",
      # Middleware
      "RequestLoggingMiddleware",
      "ErrorHandlingMiddleware",
      "RateLimitMiddleware",
      # Dependencies
      "get_db",
      "get_redis",
      "get_current_user",
      "get_gemini_client",
]

__version__ = "0.1.0"
__author__ = "ClinicalMind Team"
