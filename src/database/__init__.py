"""
ClinicalMind Database Module

This module provides database connectivity and ORM models for the
Clinical Trial Simulator. Uses SQLAlchemy for PostgreSQL integration
with async support via asyncpg.

Features:
---------
- Async database connections with connection pooling
- SQLAlchemy ORM models for all entities
- Repository pattern for data access
- Database migrations with Alembic
- Redis caching integration
"""

from .connection import (
    DatabaseConnection,
    get_database_url,
    create_engine,
    get_session,
    init_db,
)
from .models import (
    Base,
    Patient,
    Drug,
    Trial,
    Simulation,
    AdverseEvent,
    DosingRegimen,
    RegulatoryDocument,
)
from .repository import (
    BaseRepository,
    PatientRepository,
    DrugRepository,
    TrialRepository,
    SimulationRepository,
)
from .cache import (
    RedisCache,
    get_redis_client,
    cache_result,
)

__all__ = [
      # Connection
    "DatabaseConnection",
      "get_database_url",
      "create_engine",
      "get_session",
      "init_db",
      # Models
      "Base",
      "Patient",
      "Drug",
      "Trial",
      "Simulation",
      "AdverseEvent",
      "DosingRegimen",
      "RegulatoryDocument",
      # Repositories
      "BaseRepository",
      "PatientRepository",
      "DrugRepository",
      "TrialRepository",
      "SimulationRepository",
      # Cache
      "RedisCache",
      "get_redis_client",
      "cache_result",
]

__version__ = "0.1.0"
__author__ = "ClinicalMind Team"
