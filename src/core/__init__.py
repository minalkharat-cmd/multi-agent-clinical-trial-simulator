"""
Core module for ClinicalMind Clinical Trial Simulator.

Provides configuration management, logging, and utility functions.
"""

from src.core.config import settings, Settings
from src.core.logging_service import get_logger, setup_logging

__all__ = [
      "settings",
      "Settings",
      "get_logger",
      "setup_logging",
]
