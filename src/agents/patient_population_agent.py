"""
Patient Population Agent - Generates Digital Twin Patient Profiles

This agent creates synthetic patient populations with realistic demographic,
genomic, and medical history data for clinical trial simulations.

Built for Gemini 3 Hackathon - Multi-Agent Clinical Trial Simulator
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from datetime import datetime, timedelta


class Gender(Enum):
      MALE = "male"
      FEMALE = "female"
      OTHER = "other"


class Ethnicity(Enum):
      CAUCASIAN = "caucasian"
      AFRICAN_AMERICAN = "african_american"
      HISPANIC = "hispanic"
      ASIAN = "asian"
      OTHER = "other"


@dataclass
class GenomicProfile:
      """Represents a patient's genomic markers relevant to drug metabolism."""
      cyp2d6_status: str  # Poor/Intermediate/Normal/Ultra-rapid metabolizer
    cyp3a4_activity: str  # Low/Normal/High
    hla_markers: List[str] = field(default_factory=list)
    pharmacogenomic_variants: Dict[str, str] = field(default_factory=dict)


@dataclass
class MedicalHistory:
      """Patient's medical history and current conditions."""
      conditions: List[str] = field(default_factory=list)
      allergies: List[str] = field(default_factory=list)
      current_medications: List[str] = field(default_factory=list)
      previous_adverse_events: List[str] = field(default_factory=list)
      surgeries: List[str] = field(default_factory=list)


@dataclass
class VitalSigns:
      """Patient's baseline vital signs."""
      systolic_bp: float
      diastolic_bp: float
      heart_rate: float
      weight_kg: float
      height_cm: float
      bmi: float = field(init=False)

    def __post_init__(self):
              self.bmi = self.weight_kg / ((self.height_cm / 100) ** 2)


@dataclass 
class PatientProfile:
      """Complete digital twin of a patient for clinical trial simulation."""
      patient_id: str
      age: int
      gender: Gender
      ethnicity: Ethnicity
      genomic_profile: GenomicProfile
      medical_history: MedicalHistory
      vital_signs: VitalSigns
      enrollment_date: datetime

    # Trial-specific data
      arm_assignment: Optional[str] = None
      baseline_biomarkers: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
              """Convert patient profile to dictionary for serialization."""
              return {
                  "patient_id": self.patient_id,
                  "age": self.age,
                  "gender": self.gender.value,
                  "ethnicity": self.ethnicity.value,
                  "genomic_profile": {
                      "cyp2d6_status": self.genomic_profile.cyp2d6_status,
                      "cyp3a4_activity": self.genomic_profile.cyp3a4_activity,
                      "hla_markers": self.genomic_profile.hla_markers,
                      "pharmacogenomic_variants": self.genomic_profile.pharmacogenomic_variants
                  },
                  "medical_history": {
                      "conditions": self.medical_history.conditions,
                      "allergies": self.medical_history.allergies,
                      "current_medications": self.medical_history.current_medications,
                      "previous_adverse_events": self.medical_history.previous_adverse_events
                  },
                  "vital_signs": {
                      "systolic_bp": self.vital_signs.systolic_bp,
                      "diastolic_bp": self.vital_signs.diastolic_bp,
                      "heart_rate": self.vital_signs.heart_rate,
                      "weight_kg": self.vital_signs.weight_kg,
                      "height_cm": self.vital_signs.height_cm,
                      "bmi": self.vital_signs.bmi
                  },
                  "enrollment_date": self.enrollment_date.isoformat(),
                  "arm_assignment": self.arm_assignment,
                  "baseline_biomarkers": self.baseline_biomarkers
              }


class PatientPopulationAgent:
      """
          AI Agent for generating realistic patient populations using Gemini.

                  Uses Gemini 3 to generate contextually appropriate patient profiles
                      based on the trial's inclusion/exclusion criteria and target indication.
                          """

    def __init__(self, api_key: str, model_name: str = "gemini-3-pro"):
              """Initialize the agent with Gemini API credentials."""
              genai.configure(api_key=api_key)
              self.model = genai.GenerativeModel(model_name)
              self.generated_patients: List[PatientProfile] = []

    async def generate_population(
              self,
              target_indication: str,
              sample_size: int,
              inclusion_criteria: List[str],
              exclusion_criteria: List[str],
              age_range: tuple = (18, 75)
    ) -> List[PatientProfile]:
              """
                      Generate a synthetic patient population for a clinical trial.

                                      Args:
                                                  target_indication: The disease/condition being studied
                                                              sample_size: Number of patients to generate
                                                                          inclusion_criteria: List of inclusion criteria
                                                                                      exclusion_criteria: List of exclusion criteria
                                                                                                  age_range: Tuple of (min_age, max_age)
                                                                                                              
                                                                                                                      Returns:
                                                                                                                                  List of PatientProfile objects
                                                                                                                                          """
              prompt = self._build_generation_prompt(
                  target_indication, sample_size, inclusion_criteria, 
                  exclusion_criteria, age_range
              )

        response = await self.model.generate_content_async(prompt)
        patients_data = self._parse_gemini_response(response.text)

        patients = []
        for data in patients_data:
                      patient = self._create_patient_from_data(data)
                      patients.append(patient)

        self.generated_patients = patients
        return patients

    def _build_generation_prompt(
              self,
              indication: str,
              size: int,
              inclusion: List[str],
              exclusion: List[str],
              age_range: tuple
    ) -> str:
              """Build the prompt for Gemini to generate patient data."""
              return f"""You are a clinical trial simulation expert. Generate {size} realistic 
      patient profiles for a clinical trial studying {indication}.

      INCLUSION CRITERIA:
      {chr(10).join(f'- {c}' for c in inclusion)}

      EXCLUSION CRITERIA:
      {chr(10).join(f'- {c}' for c in exclusion)}

      AGE RANGE: {age_range[0]} to {age_range[1]} years

      For each patient, provide a JSON object with:
      - age, gender, ethnicity
      - genomic_profile (CYP2D6 status, CYP3A4 activity, relevant HLA markers)
      - medical_history (conditions, allergies, current medications)
      - vital_signs (BP, heart rate, weight, height)
      - relevant baseline biomarkers for {indication}

      Ensure diversity in the population and realistic correlations between demographics,
      genomics, and medical history. Return as a JSON array.
      """

    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
              """Parse Gemini's response into structured data."""
              # Extract JSON from response
              try:
                            start = response_text.find('[')
                            end = response_text.rfind(']') + 1
                            json_str = response_text[start:end]
                            return json.loads(json_str)
except (json.JSONDecodeError, ValueError):
              # Fallback: generate synthetic data
              return self._generate_fallback_data()

    def _generate_fallback_data(self) -> List[Dict]:
              """Generate synthetic patient data as fallback."""
              return [{
                  "age": random.randint(25, 70),
                  "gender": random.choice(["male", "female"]),
                  "ethnicity": random.choice(["caucasian", "african_american", "hispanic", "asian"]),
                  "cyp2d6_status": random.choice(["Poor", "Intermediate", "Normal", "Ultra-rapid"]),
                  "cyp3a4_activity": random.choice(["Low", "Normal", "High"]),
                  "conditions": ["Hypertension", "Type 2 Diabetes"],
                  "systolic_bp": random.randint(120, 160),
                  "diastolic_bp": random.randint(70, 100),
                  "heart_rate": random.randint(60, 100),
                  "weight_kg": random.randint(60, 120),
                  "height_cm": random.randint(150, 190)
              }]

    def _create_patient_from_data(self, data: Dict) -> PatientProfile:
              """Create a PatientProfile from parsed data."""
              patient_id = f"PT-{random.randint(10000, 99999)}"

        genomic = GenomicProfile(
                      cyp2d6_status=data.get("cyp2d6_status", "Normal"),
                      cyp3a4_activity=data.get("cyp3a4_activity", "Normal"),
                      hla_markers=data.get("hla_markers", []),
                      pharmacogenomic_variants=data.get("pgx_variants", {})
        )

        history = MedicalHistory(
                      conditions=data.get("conditions", []),
                      allergies=data.get("allergies", []),
                      current_medications=data.get("medications", []),
                      previous_adverse_events=data.get("adverse_events", [])
        )

        vitals = VitalSigns(
                      systolic_bp=data.get("systolic_bp", 120),
                      diastolic_bp=data.get("diastolic_bp", 80),
                      heart_rate=data.get("heart_rate", 72),
                      weight_kg=data.get("weight_kg", 70),
                      height_cm=data.get("height_cm", 170)
        )

        return PatientProfile(
                      patient_id=patient_id,
                      age=data.get("age", 45),
                      gender=Gender(data.get("gender", "male")),
                      ethnicity=Ethnicity(data.get("ethnicity", "caucasian")),
                      genomic_profile=genomic,
                      medical_history=history,
                      vital_signs=vitals,
                      enrollment_date=datetime.now(),
                      baseline_biomarkers=data.get("biomarkers", {})
        )

    def get_population_summary(self) -> Dict[str, Any]:
              """Get summary statistics of the generated population."""
              if not self.generated_patients:
                            return {}

        ages = [p.age for p in self.generated_patients]
        genders = [p.gender.value for p in self.generated_patients]

        return {
                      "total_patients": len(self.generated_patients),
                      "age_stats": {
                                        "mean": sum(ages) / len(ages),
                                        "min": min(ages),
                                        "max": max(ages)
                      },
                      "gender_distribution": {
                                        g: genders.count(g) for g in set(genders)
                      },
                      "cyp2d6_distribution": self._get_cyp2d6_distribution()
        }

    def _get_cyp2d6_distribution(self) -> Dict[str, int]:
              """Get distribution of CYP2D6 metabolizer statuses."""
              statuses = [p.genomic_profile.cyp2d6_status for p in self.generated_patients]
              return {s: statuses.count(s) for s in set(statuses)}
