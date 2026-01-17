"""
Unit tests for ClinicalMind API endpoints.

Tests cover all REST API endpoints including:
- Health checks
- Simulation management
- Patient population endpoints
- Drug interaction analysis
- Adverse event prediction
- Dosing optimization
- Regulatory document generation
"""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestHealthEndpoints:
      """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
              """Test the main health check endpoint."""
              response = await async_client.get("/health")
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert data["status"] == "healthy"
              assert "version" in data

    @pytest.mark.asyncio
    async def test_readiness_check(self, async_client: AsyncClient):
              """Test the readiness endpoint."""
              response = await async_client.get("/health/ready")
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "database" in data
              assert "redis" in data


class TestSimulationEndpoints:
      """Tests for simulation management endpoints."""

    @pytest.mark.asyncio
    async def test_create_simulation(self, async_client: AsyncClient, sample_simulation_config):
              """Test creating a new simulation."""
              response = await async_client.post(
                  "/api/v1/simulations",
                  json=sample_simulation_config
              )
              assert response.status_code == status.HTTP_201_CREATED
              data = response.json()
              assert "simulation_id" in data
              assert data["status"] == "created"

    @pytest.mark.asyncio
    async def test_get_simulation(self, async_client: AsyncClient, created_simulation):
              """Test retrieving a simulation by ID."""
              simulation_id = created_simulation["simulation_id"]
              response = await async_client.get(f"/api/v1/simulations/{simulation_id}")
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert data["simulation_id"] == simulation_id

    @pytest.mark.asyncio
    async def test_run_simulation(self, async_client: AsyncClient, created_simulation):
              """Test running a simulation."""
              simulation_id = created_simulation["simulation_id"]
              response = await async_client.post(f"/api/v1/simulations/{simulation_id}/run")
              assert response.status_code == status.HTTP_202_ACCEPTED
              data = response.json()
              assert data["status"] in ["running", "queued"]

    @pytest.mark.asyncio
    async def test_get_simulation_results(self, async_client: AsyncClient, completed_simulation):
              """Test retrieving simulation results."""
              simulation_id = completed_simulation["simulation_id"]
              response = await async_client.get(f"/api/v1/simulations/{simulation_id}/results")
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "results" in data


class TestPatientEndpoints:
      """Tests for patient population endpoints."""

    @pytest.mark.asyncio
    async def test_generate_population(self, async_client: AsyncClient):
              """Test generating a patient population."""
              response = await async_client.post(
                  "/api/v1/patients/generate",
                  json={"size": 50, "demographics": {"age_range": [18, 65]}}
              )
              assert response.status_code == status.HTTP_201_CREATED
              data = response.json()
              assert "population_id" in data
              assert data["size"] == 50

    @pytest.mark.asyncio
    async def test_get_patient(self, async_client: AsyncClient, sample_patient):
              """Test retrieving a specific patient."""
              patient_id = sample_patient["patient_id"]
              response = await async_client.get(f"/api/v1/patients/{patient_id}")
              assert response.status_code == status.HTTP_200_OK


class TestDrugEndpoints:
      """Tests for drug interaction endpoints."""

    @pytest.mark.asyncio
    async def test_analyze_interactions(self, async_client: AsyncClient):
              """Test analyzing drug interactions."""
              response = await async_client.post(
                  "/api/v1/drugs/interactions",
                  json={"drugs": ["aspirin", "warfarin", "metformin"]}
              )
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "interactions" in data

    @pytest.mark.asyncio
    async def test_get_drug_info(self, async_client: AsyncClient):
              """Test retrieving drug information."""
              response = await async_client.get("/api/v1/drugs/aspirin")
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert data["name"] == "aspirin"


class TestAdverseEventEndpoints:
      """Tests for adverse event prediction endpoints."""

    @pytest.mark.asyncio
    async def test_predict_adverse_events(self, async_client: AsyncClient, sample_patient):
              """Test predicting adverse events."""
              response = await async_client.post(
                  "/api/v1/adverse-events/predict",
                  json={
                      "patient_id": sample_patient["patient_id"],
                      "drugs": ["metformin", "lisinopril"]
                  }
              )
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "predictions" in data
              assert "risk_score" in data


class TestDosingEndpoints:
      """Tests for dosing optimization endpoints."""

    @pytest.mark.asyncio
    async def test_optimize_dose(self, async_client: AsyncClient, sample_patient):
              """Test optimizing drug dosing."""
              response = await async_client.post(
                  "/api/v1/dosing/optimize",
                  json={
                      "patient_id": sample_patient["patient_id"],
                      "drug": "metformin",
                      "target_efficacy": 0.8
                  }
              )
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "recommended_dose" in data
              assert "frequency" in data


class TestRegulatoryEndpoints:
      """Tests for regulatory document generation endpoints."""

    @pytest.mark.asyncio
    async def test_generate_fda_summary(self, async_client: AsyncClient, sample_trial_data):
              """Test generating FDA submission summary."""
              response = await async_client.post(
                  "/api/v1/regulatory/fda-summary",
                  json={"trial_data": sample_trial_data, "template": "IND"}
              )
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "document" in data

    @pytest.mark.asyncio
    async def test_compliance_check(self, async_client: AsyncClient):
              """Test regulatory compliance check."""
              response = await async_client.post(
                  "/api/v1/regulatory/compliance-check",
                  json={
                      "document_type": "clinical_study_report",
                      "content": {"sections": ["background", "methods"]}
                  }
              )
              assert response.status_code == status.HTTP_200_OK
              data = response.json()
              assert "is_compliant" in data
