"""
ClinicalMind: Multi-Agent Clinical Trial Simulator

A digital twin system for simulating clinical trials using AI agents.
"""

__version__ = "1.0.0"
__author__ = "ClinicalMind Team"
__email__ = "contact@clinicalmind.ai"

from src.core.config import settings
from src.core.logging_service import get_logger

__all__ = [
      "settings",
      "get_logger",
      "__version__",
]
