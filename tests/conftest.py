"""
Pytest Configuration and Fixtures for Clinical Trial Simulator Tests
"""

import pytest
from typing import Generator, Any
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_gemini_client() -> MagicMock:
      """Create a mock Gemini AI client for testing."""
      client = MagicMock()
      client.generate_content = AsyncMock(return_value=MagicMock(
          text="Mock AI response for testing purposes"
      ))
      return client


@pytest.fixture
def sample_patient_data() -> dict[str, Any]:
      """Sample patient data for testing."""
      return {
          "patient_id": "TEST-001",
          "age": 45,
          "gender": "female",
          "weight_kg": 65.0,
          "height_cm": 165,
          "conditions": ["hypertension", "type_2_diabetes"],
          "current_medications": ["metformin", "lisinopril"],
          "allergies": ["penicillin"],
      }


@pytest.fixture
def sample_drug_data() -> dict[str, Any]:
      """Sample drug data for testing."""
      return {
          "drug_id": "DRUG-001",
          "name": "Test Compound X",
          "mechanism": "ACE inhibitor",
          "dosage_mg": 10.0,
          "frequency": "once_daily",
          "route": "oral",
      }


@pytest.fixture
def sample_trial_config() -> dict[str, Any]:
      """Sample clinical trial configuration."""
      return {
          "trial_id": "TRIAL-2024-001",
          "phase": "Phase 2",
          "target_enrollment": 100,
          "duration_weeks": 12,
          "primary_endpoint": "blood_pressure_reduction",
          "arms": [
              {"name": "placebo", "allocation_ratio": 1},
              {"name": "low_dose", "allocation_ratio": 2},
              {"name": "high_dose", "allocation_ratio": 2},
          ],
      }


@pytest.fixture
def mock_database_session() -> Generator[MagicMock, None, None]:
      """Create a mock database session for testing."""
      session = MagicMock()
      session.commit = MagicMock()
      session.rollback = MagicMock()
      session.close = MagicMock()
      yield session


@pytest.fixture(autouse=True)
def reset_mocks(request: pytest.FixtureRequest) -> Generator[None, None, None]:
      """Reset all mocks after each test."""
      yield
      # Cleanup is automatic with pytest's fixture teardown
