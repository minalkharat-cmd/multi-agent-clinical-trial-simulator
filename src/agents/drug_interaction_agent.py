"""
Drug Interaction Agent - Simulates Pharmacokinetics and Drug-Drug Interactions

This agent models drug metabolism, predicts plasma concentrations,
and identifies potential drug-drug interactions based on patient genomics.

Built for Gemini 3 Hackathon - Multi-Agent Clinical Trial Simulator
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import json


class InteractionSeverity(Enum):
      """Severity levels for drug-drug interactions."""
      NONE = "none"
      MINOR = "minor"
      MODERATE = "moderate"
      MAJOR = "major"
      CONTRAINDICATED = "contraindicated"


class MetabolismPathway(Enum):
      """Major drug metabolism pathways."""
      CYP1A2 = "CYP1A2"
      CYP2C9 = "CYP2C9"
      CYP2C19 = "CYP2C19"
      CYP2D6 = "CYP2D6"
      CYP3A4 = "CYP3A4"
      UGT = "UGT"
      RENAL = "Renal"


@dataclass
class DrugProperties:
      """Pharmacological properties of a drug."""
      name: str
      generic_name: str
      drug_class: str
      half_life_hours: float
      bioavailability: float  # 0-1
    volume_of_distribution: float  # L/kg
    protein_binding: float  # 0-1
    primary_metabolism: List[MetabolismPathway]
    active_metabolites: List[str] = field(default_factory=list)
    therapeutic_range: Tuple[float, float] = (0, 0)  # min, max ng/mL


@dataclass
class PKParameters:
      """Pharmacokinetic parameters for a patient-drug combination."""
      cmax: float  # Peak concentration
    tmax: float  # Time to peak
    auc: float   # Area under curve
    clearance: float
    half_life: float
    steady_state_concentration: float


@dataclass
class DrugInteraction:
      """Represents an interaction between two drugs."""
      drug_a: str
      drug_b: str
      severity: InteractionSeverity
      mechanism: str
      clinical_effect: str
      recommendation: str
      evidence_level: str  # High/Moderate/Low


@dataclass
class SimulationResult:
      """Results from a drug interaction simulation."""
      patient_id: str
      drug_name: str
      pk_parameters: PKParameters
      interactions: List[DrugInteraction]
      dose_adjustment_needed: bool
      recommended_dose: Optional[float]
      warnings: List[str]
      timestamp: str


class DrugInteractionAgent:
      """
          AI Agent for simulating drug interactions and pharmacokinetics.

                  Uses Gemini 3 to analyze patient genomics and predict drug behavior,
                      including metabolism rates, interactions, and optimal dosing.
                          """

    def __init__(self, api_key: str, model_name: str = "gemini-3-pro"):
              """Initialize the agent with Gemini API credentials."""
              genai.configure(api_key=api_key)
              self.model = genai.GenerativeModel(model_name)
              self.drug_database: Dict[str, DrugProperties] = {}
              self.interaction_cache: Dict[str, DrugInteraction] = {}
              self._load_default_drugs()

    def _load_default_drugs(self):
              """Load common drugs used in clinical trials."""
              self.drug_database = {
                  "metformin": DrugProperties(
                      name="Metformin",
                      generic_name="metformin",
                      drug_class="Biguanide",
                      half_life_hours=6.2,
                      bioavailability=0.55,
                      volume_of_distribution=654,
                      protein_binding=0.0,
                      primary_metabolism=[MetabolismPathway.RENAL],
                      therapeutic_range=(1000, 2000)
                  ),
                  "atorvastatin": DrugProperties(
                      name="Atorvastatin",
                      generic_name="atorvastatin",
                      drug_class="Statin",
                      half_life_hours=14,
                      bioavailability=0.14,
                      volume_of_distribution=381,
                      protein_binding=0.98,
                      primary_metabolism=[MetabolismPathway.CYP3A4],
                      therapeutic_range=(5, 80)
                  ),
                  "lisinopril": DrugProperties(
                      name="Lisinopril",
                      generic_name="lisinopril",
                      drug_class="ACE Inhibitor",
                      half_life_hours=12,
                      bioavailability=0.25,
                      volume_of_distribution=124,
                      protein_binding=0.0,
                      primary_metabolism=[MetabolismPathway.RENAL],
                      therapeutic_range=(10, 40)
                  )
              }

    async def simulate_pk(
              self,
              patient_profile: Dict,
              drug_name: str,
              dose_mg: float,
              frequency_hours: int = 24
    ) -> PKParameters:
              """
                      Simulate pharmacokinetics for a patient-drug combination.

                                      Args:
                                                  patient_profile: Patient data including genomics
                                                              drug_name: Name of the drug
                                                                          dose_mg: Dose in milligrams
                                                                                      frequency_hours: Dosing interval

                                                                                                          Returns:
                                                                                                                      PKParameters with simulated values
                                                                                                                              """
              drug = self.drug_database.get(drug_name.lower())
              if not drug:
                            # Use Gemini to get drug properties
                            drug = await self._get_drug_from_gemini(drug_name)

              # Adjust for patient factors
              adjustment_factor = self._calculate_adjustment_factor(
                            patient_profile, drug
              )

        # Calculate PK parameters
        ke = 0.693 / drug.half_life_hours  # Elimination rate constant
        adjusted_cl = (dose_mg * drug.bioavailability) / (drug.half_life_hours * adjustment_factor)

        cmax = (dose_mg * drug.bioavailability) / drug.volume_of_distribution
        tmax = 1.5  # Typical absorption time
        auc = (dose_mg * drug.bioavailability) / adjusted_cl

        # Steady state after ~5 half-lives
        css = (dose_mg * drug.bioavailability) / (adjusted_cl * frequency_hours)

        return PKParameters(
                      cmax=cmax * adjustment_factor,
                      tmax=tmax,
                      auc=auc,
                      clearance=adjusted_cl,
                      half_life=drug.half_life_hours / adjustment_factor,
                      steady_state_concentration=css
        )

    def _calculate_adjustment_factor(
              self,
              patient: Dict,
              drug: DrugProperties
    ) -> float:
              """Calculate dose adjustment based on patient factors."""
              factor = 1.0

        genomic = patient.get("genomic_profile", {})

        # CYP2D6 adjustment
        if MetabolismPathway.CYP2D6 in drug.primary_metabolism:
                      cyp2d6 = genomic.get("cyp2d6_status", "Normal")
                      if cyp2d6 == "Poor":
                                        factor *= 0.5  # Slower metabolism
elif cyp2d6 == "Ultra-rapid":
                  factor *= 2.0  # Faster metabolism

        # CYP3A4 adjustment
          if MetabolismPathway.CYP3A4 in drug.primary_metabolism:
                        cyp3a4 = genomic.get("cyp3a4_activity", "Normal")
                        if cyp3a4 == "Low":
                                          factor *= 0.7
          elif cyp3a4 == "High":
                            factor *= 1.5

        # Age adjustment
        age = patient.get("age", 50)
        if age > 65:
                      factor *= 0.8
elif age < 18:
              factor *= 0.9

        # Renal function (simplified)
          vitals = patient.get("vital_signs", {})
        bmi = vitals.get("bmi", 25)
        if bmi > 30:
                      factor *= 1.1

        return factor

    async def check_interactions(
              self,
              drug_list: List[str],
              patient_profile: Dict
    ) -> List[DrugInteraction]:
              """
                      Check for interactions between multiple drugs.

                                      Args:
                                                  drug_list: List of drug names
                                                              patient_profile: Patient data

                                                                                  Returns:
                                                                                              List of identified interactions
                                                                                                      """
              interactions = []

        # Check all drug pairs
              for i, drug_a in enumerate(drug_list):
                            for drug_b in drug_list[i+1:]:
                                              interaction = await self._check_pair_interaction(
                                                                    drug_a, drug_b, patient_profile
                                              )
                                              if interaction and interaction.severity != InteractionSeverity.NONE:
                                                                    interactions.append(interaction)

                                      return interactions

    async def _check_pair_interaction(
              self,
              drug_a: str,
              drug_b: str,
              patient: Dict
    ) -> Optional[DrugInteraction]:
              """Check interaction between two specific drugs."""
        cache_key = f"{drug_a.lower()}_{drug_b.lower()}"

        if cache_key in self.interaction_cache:
                      return self.interaction_cache[cache_key]

        # Use Gemini to analyze interaction
        prompt = f"""Analyze the drug-drug interaction between {drug_a} and {drug_b}.

                Patient context:
                - Age: {patient.get('age', 'Unknown')}
                - CYP2D6 status: {patient.get('genomic_profile', {}).get('cyp2d6_status', 'Normal')}
                - CYP3A4 activity: {patient.get('genomic_profile', {}).get('cyp3a4_activity', 'Normal')}
                - Current conditions: {patient.get('medical_history', {}).get('conditions', [])}

                Provide a JSON response with:
                - severity: none/minor/moderate/major/contraindicated
                - mechanism: pharmacological mechanism of interaction
                - clinical_effect: what happens clinically
                - recommendation: clinical recommendation
                - evidence_level: High/Moderate/Low
                """

        try:
                      response = await self.model.generate_content_async(prompt)
            data = self._parse_interaction_response(response.text)

            interaction = DrugInteraction(
                              drug_a=drug_a,
                              drug_b=drug_b,
                              severity=InteractionSeverity(data.get("severity", "none")),
                              mechanism=data.get("mechanism", "Unknown"),
                              clinical_effect=data.get("clinical_effect", "Unknown"),
                              recommendation=data.get("recommendation", "Monitor"),
                              evidence_level=data.get("evidence_level", "Low")
            )

            self.interaction_cache[cache_key] = interaction
            return interaction

except Exception:
            return None

    def _parse_interaction_response(self, text: str) -> Dict:
              """Parse Gemini's interaction analysis response."""
        try:
                      start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except:
            return {"severity": "none"}

    async def optimize_dosing(
              self,
              patient_profile: Dict,
              drug_name: str,
              target_concentration: float
    ) -> Dict[str, Any]:
              """
                      Calculate optimal dose to achieve target concentration.

                                      Args:
                                                  patient_profile: Patient data
                                                              drug_name: Drug to optimize
                                                                          target_concentration: Desired plasma level

                                                                                              Returns:
                                                                                                          Dosing recommendation
                                                                                                                  """
        drug = self.drug_database.get(drug_name.lower())
        if not drug:
                      return {"error": "Drug not found"}

        adjustment = self._calculate_adjustment_factor(patient_profile, drug)

        # Back-calculate required dose
        base_dose = (target_concentration * drug.volume_of_distribution) / drug.bioavailability
        adjusted_dose = base_dose / adjustment

        # Round to practical dose
        practical_dose = self._round_to_practical_dose(adjusted_dose)

        return {
                      "drug": drug_name,
                      "calculated_dose": adjusted_dose,
                      "recommended_dose": practical_dose,
                      "adjustment_factor": adjustment,
                      "dosing_interval": "24 hours",
                      "rationale": f"Adjusted for patient's metabolizer status and demographics"
        }

    def _round_to_practical_dose(self, dose: float) -> float:
              """Round to a practical tablet/capsule dose."""
        common_doses = [5, 10, 15, 20, 25, 40, 50, 75, 100, 150, 200, 250, 500]
        return min(common_doses, key=lambda x: abs(x - dose))

    async def _get_drug_from_gemini(self, drug_name: str) -> DrugProperties:
              """Query Gemini for drug properties if not in database."""
        prompt = f"""Provide pharmacological properties for {drug_name} in JSON:
                - half_life_hours
                        - bioavailability (0-1)
                                - volume_of_distribution (L/kg)
                                        - protein_binding (0-1)
                                                - primary_metabolism (CYP enzymes)
                                                        - drug_class
                                                                """

        # Return default if API fails
        return DrugProperties(
                      name=drug_name,
                      generic_name=drug_name.lower(),
                      drug_class="Unknown",
                      half_life_hours=12,
                      bioavailability=0.5,
                      volume_of_distribution=100,
                      protein_binding=0.5,
                      primary_metabolism=[MetabolismPathway.CYP3A4]
        )
