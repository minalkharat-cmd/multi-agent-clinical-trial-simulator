"""
Unit tests for ClinicalMind Agent modules.

Tests cover all agent implementations including:
- Population Agent
- Drug Interaction Agent
- Adverse Event Agent
- Dosing Agent
- Regulatory Agent
- Orchestrator Agent
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


class TestPopulationAgent:
      """Tests for the Population Agent."""

    @pytest.fixture
    def population_agent(self, mock_gemini_client):
              """Create a Population Agent instance for testing."""
              from src.agents import PopulationAgent
              return PopulationAgent(gemini_client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_generate_patient_population(self, population_agent):
              """Test generating a virtual patient population."""
              population = await population_agent.generate_population(
                  size=100,
                  demographics={"age_range": (18, 65), "gender_ratio": 0.5}
              )
              assert population is not None
              assert len(population.patients) == 100

    @pytest.mark.asyncio
    async def test_population_stratification(self, population_agent):
              """Test stratifying population by criteria."""
              result = await population_agent.stratify(
                  population_id="test-pop-001",
                  criteria=["age", "gender", "comorbidities"]
              )
              assert "strata" in result
              assert len(result["strata"]) > 0


class TestDrugInteractionAgent:
      """Tests for the Drug Interaction Agent."""

    @pytest.fixture
    def drug_agent(self, mock_gemini_client):
              """Create a Drug Interaction Agent instance."""
              from src.agents import DrugInteractionAgent
              return DrugInteractionAgent(gemini_client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_analyze_drug_interactions(self, drug_agent):
              """Test analyzing drug-drug interactions."""
              interactions = await drug_agent.analyze_interactions(
                  drugs=["aspirin", "warfarin", "metformin"]
              )
              assert interactions is not None
              assert "interaction_matrix" in interactions

    @pytest.mark.asyncio
    async def test_predict_metabolic_pathways(self, drug_agent):
              """Test predicting drug metabolic pathways."""
              pathways = await drug_agent.predict_pathways(drug_name="ibuprofen")
              assert pathways is not None
              assert "cyp_enzymes" in pathways


class TestAdverseEventAgent:
      """Tests for the Adverse Event Agent."""

    @pytest.fixture
    def ae_agent(self, mock_gemini_client):
              """Create an Adverse Event Agent instance."""
              from src.agents import AdverseEventAgent
              return AdverseEventAgent(gemini_client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_predict_adverse_events(self, ae_agent, sample_patient):
              """Test predicting adverse events for a patient."""
              predictions = await ae_agent.predict(
                  patient=sample_patient,
                  drugs=["metformin", "lisinopril"]
              )
              assert predictions is not None
              assert "risk_score" in predictions
              assert 0 <= predictions["risk_score"] <= 1

    @pytest.mark.asyncio
    async def test_classify_event_severity(self, ae_agent):
              """Test classifying adverse event severity."""
              classification = await ae_agent.classify_severity(
                  event_description="mild headache after medication"
              )
              assert classification in ["mild", "moderate", "severe", "life-threatening"]


class TestDosingAgent:
      """Tests for the Dosing Optimization Agent."""

    @pytest.fixture
    def dosing_agent(self, mock_gemini_client):
              """Create a Dosing Agent instance."""
              from src.agents import DosingAgent
              return DosingAgent(gemini_client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_optimize_dosing(self, dosing_agent, sample_patient):
              """Test optimizing drug dosing for a patient."""
              recommendation = await dosing_agent.optimize(
                  patient=sample_patient,
                  drug="metformin",
                  target_efficacy=0.8
              )
              assert recommendation is not None
              assert "dose" in recommendation
              assert "frequency" in recommendation

    @pytest.mark.asyncio
    async def test_calculate_pk_parameters(self, dosing_agent):
              """Test calculating pharmacokinetic parameters."""
              pk_params = await dosing_agent.calculate_pk(
                  drug="aspirin",
                  patient_weight=70,
                  renal_function="normal"
              )
              assert "half_life" in pk_params
              assert "clearance" in pk_params


class TestRegulatoryAgent:
      """Tests for the Regulatory Document Agent."""

    @pytest.fixture
    def regulatory_agent(self, mock_gemini_client):
              """Create a Regulatory Agent instance."""
              from src.agents import RegulatoryAgent
              return RegulatoryAgent(gemini_client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_generate_fda_summary(self, regulatory_agent, sample_trial_data):
              """Test generating FDA submission summary."""
              document = await regulatory_agent.generate_fda_summary(
                  trial_data=sample_trial_data,
                  template="IND"
              )
              assert document is not None
              assert "executive_summary" in document
              assert "safety_data" in document

    @pytest.mark.asyncio
    async def test_compliance_check(self, regulatory_agent):
              """Test checking regulatory compliance."""
              compliance = await regulatory_agent.check_compliance(
                  document_type="clinical_study_report",
                  content={"sections": ["background", "methods", "results"]}
              )
              assert "is_compliant" in compliance
              assert "missing_sections" in compliance


class TestOrchestratorAgent:
      """Tests for the Orchestrator Agent."""

    @pytest.fixture
    def orchestrator(self, mock_gemini_client):
              """Create an Orchestrator Agent instance."""
              from src.agents import OrchestratorAgent
              return OrchestratorAgent(gemini_client=mock_gemini_client)

    @pytest.mark.asyncio
    async def test_run_full_simulation(self, orchestrator, sample_simulation_config):
              """Test running a complete clinical trial simulation."""
              results = await orchestrator.run_simulation(config=sample_simulation_config)
              assert results is not None
              assert "simulation_id" in results
              assert "status" in results
              assert results["status"] == "completed"

    @pytest.mark.asyncio
    async def test_coordinate_agents(self, orchestrator):
              """Test agent coordination workflow."""
              workflow = await orchestrator.coordinate(
                  agents=["population", "drug_interaction", "adverse_event"],
                  task="safety_analysis"
              )
              assert workflow is not None
              assert "workflow_id" in workflow
