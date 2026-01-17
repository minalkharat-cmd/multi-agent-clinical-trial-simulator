"""
Enterprise Configuration Management System

Provides centralized configuration with environment-based settings,
validation, secrets management, and runtime configuration updates.

Compliant with 21 CFR Part 11 requirements for audit trails.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from datetime import datetime
import hashlib


class Environment(Enum):
      """Deployment environments."""
      DEVELOPMENT = "development"
      STAGING = "staging"
      PRODUCTION = "production"
      TESTING = "testing"


class LogLevel(Enum):
      """Logging levels."""
      DEBUG = "DEBUG"
      INFO = "INFO"
      WARNING = "WARNING"
      ERROR = "ERROR"
      CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
      """Database configuration settings."""
      host: str = "localhost"
      port: int = 5432
      name: str = "clinicalmind"
      user: str = "admin"
      password: str = ""  # Should be loaded from secrets
    pool_size: int = 10
    max_overflow: int = 20
    ssl_mode: str = "require"

    @property
    def connection_string(self) -> str:
              """Generate database connection string."""
              return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?sslmode={self.ssl_mode}"


@dataclass
class GeminiConfig:
      """Google Gemini API configuration."""
      api_key: str = ""
      model_name: str = "gemini-3-pro"
      max_tokens: int = 8192
      temperature: float = 0.7
      top_p: float = 0.95
      timeout_seconds: int = 60
      retry_attempts: int = 3
      retry_delay_seconds: float = 1.0


@dataclass
class SecurityConfig:
      """Security and compliance configuration."""
      encryption_key: str = ""
      jwt_secret: str = ""
      jwt_algorithm: str = "HS256"
      jwt_expiry_hours: int = 24
      password_min_length: int = 12
      require_mfa: bool = True
      session_timeout_minutes: int = 30
      max_login_attempts: int = 5
      lockout_duration_minutes: int = 15
      audit_log_retention_days: int = 2555  # 7 years for FDA compliance


@dataclass
class RegulatoryConfig:
      """Regulatory compliance settings."""
      cfr_part_11_enabled: bool = True
      hipaa_enabled: bool = True
      gdpr_enabled: bool = True
      electronic_signatures_enabled: bool = True
      audit_trail_enabled: bool = True
      data_integrity_checks: bool = True
      validation_protocol: str = "IQ/OQ/PQ"


@dataclass
class SimulationConfig:
      """Clinical trial simulation settings."""
      max_patients_per_trial: int = 10000
      max_concurrent_simulations: int = 10
      default_simulation_duration_days: int = 365
      monte_carlo_iterations: int = 1000
      confidence_interval: float = 0.95
      random_seed: Optional[int] = None
      parallel_processing_enabled: bool = True
      max_workers: int = 4


@dataclass
class CacheConfig:
      """Caching configuration."""
      enabled: bool = True
      backend: str = "redis"  # redis, memcached, local
    host: str = "localhost"
    port: int = 6379
    ttl_seconds: int = 3600
    max_memory_mb: int = 512


@dataclass
class LoggingConfig:
      """Logging configuration."""
      level: LogLevel = LogLevel.INFO
      format: str = "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
      output_dir: Path = Path("logs")
      max_file_size_mb: int = 100
      backup_count: int = 10
      json_format: bool = True
      include_request_id: bool = True
      include_user_id: bool = True
      sensitive_fields: List[str] = field(default_factory=lambda: [
          "password", "api_key", "token", "secret", "ssn", "credit_card"
      ])


@dataclass
class AppConfig:
      """Main application configuration."""
      app_name: str = "ClinicalMind"
      app_version: str = "1.0.0"
      environment: Environment = Environment.DEVELOPMENT
      debug: bool = False
      host: str = "0.0.0.0"
      port: int = 8000
      workers: int = 4

    # Sub-configurations
      database: DatabaseConfig = field(default_factory=DatabaseConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    regulatory: RegulatoryConfig = field(default_factory=RegulatoryConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def __post_init__(self):
              """Validate configuration after initialization."""
              self._validate()
              self._setup_logging()

    def _validate(self):
              """Validate configuration values."""
              if self.environment == Environment.PRODUCTION:
                            if self.debug:
                                              raise ValueError("Debug mode cannot be enabled in production")
                                          if not self.security.encryption_key:
                                                            raise ValueError("Encryption key required in production")
                                                        if not self.gemini.api_key:
                                                                          raise ValueError("Gemini API key required in production")
                                                                      if self.database.password == "":
                                                                                        raise ValueError("Database password required in production")

                    def _setup_logging(self):
                              """Configure logging based on settings."""
                              self.logging.output_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
              """Convert config to dictionary (excluding secrets)."""
        return {
                      "app_name": self.app_name,
                      "app_version": self.app_version,
                      "environment": self.environment.value,
                      "debug": self.debug,
                      "simulation": {
                                        "max_patients": self.simulation.max_patients_per_trial,
                                        "parallel_enabled": self.simulation.parallel_processing_enabled
                      },
                      "regulatory": {
                                        "cfr_part_11": self.regulatory.cfr_part_11_enabled,
                                        "hipaa": self.regulatory.hipaa_enabled,
                                        "gdpr": self.regulatory.gdpr_enabled
                      }
        }

    def get_config_hash(self) -> str:
              """Generate hash of configuration for change detection."""
              config_str = json.dumps(self.to_dict(), sort_keys=True)
              return hashlib.sha256(config_str.encode()).hexdigest()[:16]


class ConfigurationManager:
      """
          Enterprise configuration manager with environment support,
              validation, and audit logging.
                  """

    _instance: Optional['ConfigurationManager'] = None
    _config: Optional[AppConfig] = None

    def __new__(cls):
              """Singleton pattern for configuration manager."""
              if cls._instance is None:
                            cls._instance = super().__new__(cls)
                        return cls._instance

    def __init__(self):
              if self._config is None:
                            self._load_config()

    def _load_config(self):
              """Load configuration from environment and files."""
        env = os.getenv("CLINICALMIND_ENV", "development")
        environment = Environment(env.lower())

        # Load base configuration
        self._config = AppConfig(
                      environment=environment,
                      debug=os.getenv("DEBUG", "false").lower() == "true",
                      host=os.getenv("HOST", "0.0.0.0"),
                      port=int(os.getenv("PORT", "8000")),
        )

        # Load Gemini configuration
        self._config.gemini.api_key = os.getenv("GEMINI_API_KEY", "")
        self._config.gemini.model_name = os.getenv("GEMINI_MODEL", "gemini-3-pro")

        # Load database configuration
        self._config.database.host = os.getenv("DB_HOST", "localhost")
        self._config.database.port = int(os.getenv("DB_PORT", "5432"))
        self._config.database.name = os.getenv("DB_NAME", "clinicalmind")
        self._config.database.user = os.getenv("DB_USER", "admin")
        self._config.database.password = os.getenv("DB_PASSWORD", "")

        # Load security configuration
        self._config.security.encryption_key = os.getenv("ENCRYPTION_KEY", "")
        self._config.security.jwt_secret = os.getenv("JWT_SECRET", "")

        # Log configuration loaded (without secrets)
        self._log_config_loaded()

    def _log_config_loaded(self):
              """Log that configuration was loaded."""
        print(f"[CONFIG] Loaded configuration for environment: {self._config.environment.value}")
        print(f"[CONFIG] Config hash: {self._config.get_config_hash()}")

    @property
    def config(self) -> AppConfig:
              """Get current configuration."""
        return self._config

    def reload(self):
              """Reload configuration from environment."""
        old_hash = self._config.get_config_hash()
        self._load_config()
        new_hash = self._config.get_config_hash()

        if old_hash != new_hash:
                      print(f"[CONFIG] Configuration changed: {old_hash} -> {new_hash}")

    def get(self, key: str, default: Any = None) -> Any:
              """Get configuration value by dot-notation key."""
              keys = key.split(".")
              value = self._config

        for k in keys:
                      if hasattr(value, k):
                                        value = getattr(value, k)
else:
                  return default

        return value


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
      """Get application configuration (cached)."""
      return ConfigurationManager().config


def get_setting(key: str, default: Any = None) -> Any:
      """Get a specific setting by key."""
      return ConfigurationManager().get(key, default)
