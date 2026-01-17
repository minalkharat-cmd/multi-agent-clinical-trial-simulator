"""
Adverse Event Predictor Agent - Predicts Side Effects and Safety Signals

This agent analyzes patient profiles, drug data, and genomics to predict
potential adverse events and generate safety reports for clinical trials.

Built for Gemini 3 Hackathon - Multi-Agent Clinical Trial Simulator
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json


class AESeverity(Enum):
      """Adverse event severity grades (CTCAE)."""
      MILD = 1
      MODERATE = 2
      SEVERE = 3
      LIFE_THREATENING = 4
      DEATH = 5


class AECategory(Enum):
      """Categories of adverse events."""
      CARDIAC = "Cardiac disorders"
      GASTROINTESTINAL = "Gastrointestinal disorders"
      HEPATIC = "Hepatobiliary disorders"
      RENAL = "Renal disorders"
      NEUROLOGICAL = "Nervous system disorders"
      DERMATOLOGICAL = "Skin disorders"
      HEMATOLOGICAL = "Blood disorders"
      METABOLIC = "Metabolism disorders"
      MUSCULOSKELETAL = "Musculoskeletal disorders"
      RESPIRATORY = "Respiratory disorders"
      OTHER = "Other"


class Causality(Enum):
      """Relationship of AE to study drug."""
      DEFINITE = "Definite"
      PROBABLE = "Probable"
      POSSIBLE = "Possible"
      UNLIKELY = "Unlikely"
      UNRELATED = "Unrelated"


@dataclass
class AdverseEvent:
      """Represents a predicted or observed adverse event."""
      event_id: str
      patient_id: str
      event_name: str
      category: AECategory
      severity: AESeverity
      probability: float  # 0-1 likelihood
    onset_day: int  # Days from treatment start
    duration_days: int
    causality: Causality
    risk_factors: List[str]
    mitigation_strategies: List[str]
    is_serious: bool = False
    requires_discontinuation: bool = False


@dataclass
class SafetySignal:
      """A pattern indicating potential safety concern."""
      signal_name: str
      affected_patients: int
      total_patients: int
      incidence_rate: float
      expected_rate: float
      signal_strength: float  # PRR or similar metric
    events: List[AdverseEvent]
    recommendation: str


@dataclass
class SafetyReport:
      """Comprehensive safety report for a trial."""
      report_id: str
      trial_name: str
      report_date: datetime
      total_patients: int
      patients_with_ae: int
      total_events: int
      serious_events: int
      events_by_category: Dict[str, int]
      events_by_severity: Dict[int, int]
      safety_signals: List[SafetySignal]
      overall_safety_assessment: str


class AdverseEventAgent:
      """
          AI Agent for predicting adverse events in clinical trials.

                  Uses Gemini 3 to analyze patient data and predict potential side effects
                      based on drug properties, patient genomics, and medical history.
                          """

    def __init__(self, api_key: str, model_name: str = "gemini-3-pro"):
              """Initialize the agent with Gemini API credentials."""
              genai.configure(api_key=api_key)
              self.model = genai.GenerativeModel(model_name)
              self.known_aes: Dict[str, List[Dict]] = {}
              self.predicted_events: List[AdverseEvent] = []
              self._load_known_adverse_events()

    def _load_known_adverse_events(self):
              """Load database of known adverse events for common drugs."""
              self.known_aes = {
                  "metformin": [
                      {"name": "Nausea", "category": "GASTROINTESTINAL", "incidence": 0.25, "severity": 1},
                      {"name": "Diarrhea", "category": "GASTROINTESTINAL", "incidence": 0.15, "severity": 1},
                      {"name": "Lactic acidosis", "category": "METABOLIC", "incidence": 0.001, "severity": 4}
                  ],
                  "atorvastatin": [
                      {"name": "Myalgia", "category": "MUSCULOSKELETAL", "incidence": 0.05, "severity": 1},
                      {"name": "Elevated LFTs", "category": "HEPATIC", "incidence": 0.02, "severity": 2},
                      {"name": "Rhabdomyolysis", "category": "MUSCULOSKELETAL", "incidence": 0.0001, "severity": 4}
                  ],
                  "lisinopril": [
                      {"name": "Dry cough", "category": "RESPIRATORY", "incidence": 0.10, "severity": 1},
                      {"name": "Hyperkalemia", "category": "METABOLIC", "incidence": 0.03, "severity": 2},
                      {"name": "Angioedema", "category": "OTHER", "incidence": 0.001, "severity": 4}
                  ]
              }

    async def predict_adverse_events(
              self,
              patient_profile: Dict,
              drug_name: str,
              dose_mg: float,
              treatment_duration_days: int
    ) -> List[AdverseEvent]:
              """
                      Predict potential adverse events for a patient on treatment.

                                      Args:
                                                  patient_profile: Patient data including genomics
                                                              drug_name: Name of study drug
                                                                          dose_mg: Daily dose
                                                                                      treatment_duration_days: Expected treatment duration

                                                                                                          Returns:
                                                                                                                      List of predicted adverse events
                                                                                                                              """
              events = []

        # Get known AEs for the drug
              known = self.known_aes.get(drug_name.lower(), [])

        # Adjust risk based on patient factors
        for ae_data in known:
                      risk_multiplier = self._calculate_risk_multiplier(
                                        patient_profile, ae_data, drug_name
                      )
                      adjusted_probability = min(ae_data["incidence"] * risk_multiplier, 1.0)

            if adjusted_probability > 0.01:  # Only include if >1% risk
                              event = AdverseEvent(
                                                    event_id=f"AE-{patient_profile.get('patient_id', 'UNK')}-{len(events)+1}",
                                                    patient_id=patient_profile.get("patient_id", "Unknown"),
                                                    event_name=ae_data["name"],
                                                    category=AECategory[ae_data["category"]],
                                                    severity=AESeverity(ae_data["severity"]),
                                                    probability=adjusted_probability,
                                                    onset_day=self._estimate_onset(ae_data),
                                                    duration_days=self._estimate_duration(ae_data),
                                                    causality=Causality.PROBABLE,
                                                    risk_factors=self._identify_risk_factors(patient_profile, ae_data),
                                                    mitigation_strategies=self._get_mitigation(ae_data),
                                                    is_serious=ae_data["severity"] >= 3,
                                                    requires_discontinuation=ae_data["severity"] >= 4
                              )
                              events.append(event)

        # Use Gemini for personalized risk assessment
        gemini_events = await self._gemini_risk_assessment(
                      patient_profile, drug_name, dose_mg
        )
        events.extend(gemini_events)

        self.predicted_events.extend(events)
        return events

    def _calculate_risk_multiplier(
              self,
              patient: Dict,
              ae_data: Dict,
              drug_name: str
    ) -> float:
              """Calculate patient-specific risk multiplier."""
              multiplier = 1.0

        # Age factor
              age = patient.get("age", 50)
        if age > 65:
                      multiplier *= 1.3
elif age > 75:
              multiplier *= 1.5

        # Genomic factors
          genomic = patient.get("genomic_profile", {})

        # Poor metabolizers at higher risk for dose-dependent AEs
        if genomic.get("cyp2d6_status") == "Poor":
                      multiplier *= 1.4

        # Medical history factors
        history = patient.get("medical_history", {})
        conditions = history.get("conditions", [])

        # Renal impairment increases risk
        if "Chronic Kidney Disease" in conditions:
                      multiplier *= 1.5

        # Hepatic impairment
        if any("hepat" in c.lower() or "liver" in c.lower() for c in conditions):
                      if ae_data["category"] == "HEPATIC":
                                        multiplier *= 2.0

                  # Previous adverse events
                  previous_aes = history.get("previous_adverse_events", [])
        if ae_data["name"] in previous_aes:
                      multiplier *= 3.0  # Much higher risk if had before

        return multiplier

    def _estimate_onset(self, ae_data: Dict) -> int:
              """Estimate typical onset time in days."""
              severity = ae_data.get("severity", 1)
              category = ae_data.get("category", "OTHER")

        # GI events usually early
              if category == "GASTROINTESTINAL":
                            return 3
                        # Hepatic events take time
elif category == "HEPATIC":
              return 30
          # Skin reactions relatively quick
elif category == "DERMATOLOGICAL":
              return 7
else:
              return 14

    def _estimate_duration(self, ae_data: Dict) -> int:
              """Estimate typical duration in days."""
              severity = ae_data.get("severity", 1)
              if severity <= 2:
                            return 7
elif severity == 3:
            return 21
else:
            return 60

    def _identify_risk_factors(self, patient: Dict, ae_data: Dict) -> List[str]:
              """Identify patient-specific risk factors."""
              factors = []

        age = patient.get("age", 50)
        if age > 65:
                      factors.append(f"Advanced age ({age} years)")

        genomic = patient.get("genomic_profile", {})
        if genomic.get("cyp2d6_status") == "Poor":
                      factors.append("Poor CYP2D6 metabolizer")

        history = patient.get("medical_history", {})
        if history.get("previous_adverse_events"):
                      factors.append("History of adverse drug reactions")

        return factors if factors else ["No specific risk factors identified"]

    def _get_mitigation(self, ae_data: Dict) -> List[str]:
              """Get mitigation strategies for an adverse event."""
              strategies = {
                  "GASTROINTESTINAL": ["Take with food", "Start with low dose", "Consider antiemetics"],
                  "HEPATIC": ["Monitor LFTs regularly", "Avoid alcohol", "Review hepatotoxic meds"],
                  "MUSCULOSKELETAL": ["Monitor CK levels", "Report muscle pain", "Consider dose reduction"],
                  "METABOLIC": ["Regular metabolic panels", "Dietary counseling"],
                  "RESPIRATORY": ["Consider alternative agent if persistent", "Monitor symptoms"]
              }
              category = ae_data.get("category", "OTHER")
              return strategies.get(category, ["Clinical monitoring"])

    async def _gemini_risk_assessment(
              self,
              patient: Dict,
              drug: str,
              dose: float
    ) -> List[AdverseEvent]:
              """Use Gemini for additional personalized risk assessment."""
              prompt = f"""Analyze adverse event risk for this patient:

      Patient: Age {patient.get('age')}, {patient.get('gender', {}).get('value', 'unknown')} gender
      Genomics: CYP2D6 {patient.get('genomic_profile', {}).get('cyp2d6_status', 'Normal')}
      Conditions: {patient.get('medical_history', {}).get('conditions', [])}
      Current meds: {patient.get('medical_history', {}).get('current_medications', [])}

      Drug: {drug} at {dose}mg daily

      Identify any additional adverse events not covered by standard databases.
      Consider pharmacogenomic interactions and drug-disease interactions.

      Return JSON array with: name, category, probability (0-1), severity (1-5), rationale
      """

        try:
                      response = await self.model.generate_content_async(prompt)
                      return self._parse_gemini_aes(response.text, patient.get("patient_id", "UNK"))
                  except:
            return []

                        def _parse_gemini_aes(self, text: str, patient_id: str) -> List[AdverseEvent]:
                                  """Parse Gemini's adverse event predictions."""
                                  events = []
                                  try:
                                                start = text.find('[')
                                                end = text.rfind(']') + 1
                                                data = json.loads(text[start:end])

            for i, item in enumerate(data):
                              event = AdverseEvent(
                                                    event_id=f"AE-{patient_id}-G{i+1}",
                                                    patient_id=patient_id,
                                                    event_name=item.get("name", "Unknown"),
                                                    category=AECategory.OTHER,
                                                    severity=AESeverity(item.get("severity", 1)),
                                                    probability=item.get("probability", 0.05),
                                                    onset_day=14,
                                                    duration_days=7,
                                                    causality=Causality.POSSIBLE,
                                                    risk_factors=[item.get("rationale", "AI-identified risk")],
                                                    mitigation_strategies=["Clinical monitoring"]
                              )
                              events.append(event)
                      except:
            pass
        return events

    def generate_safety_report(
              self,
              trial_name: str,
              all_patients: List[Dict],
              all_events: List[AdverseEvent]
    ) -> SafetyReport:
              """Generate comprehensive safety report."""
              patients_with_ae = len(set(e.patient_id for e in all_events))

        # Count by category
              by_category = {}
        for event in all_events:
                      cat = event.category.value
                      by_category[cat] = by_category.get(cat, 0) + 1

        # Count by severity
        by_severity = {}
        for event in all_events:
                      sev = event.severity.value
                      by_severity[sev] = by_severity.get(sev, 0) + 1

        serious_count = sum(1 for e in all_events if e.is_serious)

        return SafetyReport(
                      report_id=f"SR-{datetime.now().strftime('%Y%m%d%H%M')}",
                      trial_name=trial_name,
                      report_date=datetime.now(),
                      total_patients=len(all_patients),
                      patients_with_ae=patients_with_ae,
                      total_events=len(all_events),
                      serious_events=serious_count,
                      events_by_category=by_category,
                      events_by_severity=by_severity,
                      safety_signals=[],  # Would be populated by signal detection
                      overall_safety_assessment=self._assess_overall_safety(all_events, len(all_patients))
        )

    def _assess_overall_safety(self, events: List[AdverseEvent], n_patients: int) -> str:
              """Generate overall safety assessment text."""
              if not events:
                            return "No adverse events observed. Safety profile appears favorable."

              serious = sum(1 for e in events if e.is_serious)
              ae_rate = len(events) / max(n_patients, 1)

        if serious == 0 and ae_rate < 0.2:
                      return "Favorable safety profile with mild adverse events only."
elif serious > 0 and serious / max(n_patients, 1) < 0.05:
            return "Generally acceptable safety with rare serious events requiring monitoring."
else:
            return "Safety concerns identified. Close monitoring and possible protocol amendment recommended."
