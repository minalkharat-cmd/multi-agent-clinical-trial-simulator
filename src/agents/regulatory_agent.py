"""
Regulatory Document Agent - Generates FDA Submission Documents

This agent creates regulatory-compliant documents including Clinical Study
Reports, IND applications, and safety summaries using Gemini AI.

Built for Gemini 3 Hackathon - Multi-Agent Clinical Trial Simulator
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class DocumentType(Enum):
      """Types of regulatory documents."""
      CLINICAL_STUDY_REPORT = "Clinical Study Report (CSR)"
      IND_SUMMARY = "IND Summary"
      SAFETY_UPDATE = "Safety Update Report"
      PROTOCOL_SYNOPSIS = "Protocol Synopsis"
      INVESTIGATOR_BROCHURE = "Investigator Brochure"
      PATIENT_NARRATIVE = "Patient Narrative"


class RegulatoryRegion(Enum):
      """Regulatory regions for compliance."""
      FDA = "FDA (United States)"
      EMA = "EMA (European Union)"
      PMDA = "PMDA (Japan)"
      ICH = "ICH Guidelines"


@dataclass
class DocumentSection:
      """A section within a regulatory document."""
      section_number: str
      title: str
      content: str
      subsections: List['DocumentSection'] = field(default_factory=list)


@dataclass
class RegulatoryDocument:
      """Complete regulatory document."""
      document_id: str
      document_type: DocumentType
      title: str
      version: str
      created_date: datetime
      trial_id: str
      sponsor: str
      sections: List[DocumentSection]
      compliance_region: RegulatoryRegion
      word_count: int = 0

    def to_markdown(self) -> str:
              """Convert document to Markdown format."""
              md = f"# {self.title}\\n\\n"
              md += f"**Document ID:** {self.document_id}\\n"
              md += f"**Version:** {self.version}\\n"
              md += f"**Date:** {self.created_date.strftime('%Y-%m-%d')}\\n"
              md += f"**Compliance:** {self.compliance_region.value}\\n\\n"
              md += "---\\n\\n"

        for section in self.sections:
                      md += self._section_to_md(section, level=2)

        return md

    def _section_to_md(self, section: DocumentSection, level: int) -> str:
              """Convert a section to Markdown."""
              prefix = "#" * level
              md = f"{prefix} {section.section_number} {section.title}\\n\\n"
              md += f"{section.content}\\n\\n"

        for sub in section.subsections:
                      md += self._section_to_md(sub, level + 1)

        return md


class RegulatoryDocumentAgent:
      """
          AI Agent for generating FDA-compliant regulatory documents.

                  Uses Gemini 3 to draft clinical study reports, safety summaries,
                      and other regulatory documents following ICH/FDA guidelines.
                          """

    def __init__(self, api_key: str, model_name: str = "gemini-3-pro"):
              """Initialize the agent with Gemini API credentials."""
              genai.configure(api_key=api_key)
              self.model = genai.GenerativeModel(model_name)
              self.generated_documents: List[RegulatoryDocument] = []

    async def generate_clinical_study_report(
              self,
              trial_data: Dict[str, Any],
              patient_summaries: List[Dict],
              safety_data: Dict,
              efficacy_results: Dict
    ) -> RegulatoryDocument:
              """
                      Generate a Clinical Study Report (CSR) following ICH E3 guidelines.

                                      Args:
                                                  trial_data: Trial metadata and protocol information
                                                              patient_summaries: Summary of patient demographics and disposition
                                                                          safety_data: Safety analysis results
                                                                                      efficacy_results: Efficacy endpoint results

                                                                                                          Returns:
                                                                                                                      Complete CSR document
                                                                                                                              """
              sections = []

        # Section 1: Title Page and Synopsis
              synopsis = await self._generate_synopsis(trial_data, efficacy_results)
        sections.append(DocumentSection("1", "Synopsis", synopsis))

        # Section 2: Table of Contents (placeholder)
        sections.append(DocumentSection("2", "Table of Contents", "[Auto-generated]"))

        # Section 3: Introduction
        intro = await self._generate_introduction(trial_data)
        sections.append(DocumentSection("3", "Introduction", intro))

        # Section 4: Study Objectives
        objectives = self._format_objectives(trial_data)
        sections.append(DocumentSection("4", "Study Objectives", objectives))

        # Section 5: Investigational Plan
        plan = await self._generate_study_plan(trial_data)
        sections.append(DocumentSection("5", "Investigational Plan", plan))

        # Section 6: Study Patients
        patients = self._format_patient_summary(patient_summaries)
        sections.append(DocumentSection("6", "Study Patients", patients))

        # Section 7: Efficacy Evaluation
        efficacy = await self._generate_efficacy_section(efficacy_results)
        sections.append(DocumentSection("7", "Efficacy Evaluation", efficacy))

        # Section 8: Safety Evaluation
        safety = await self._generate_safety_section(safety_data)
        sections.append(DocumentSection("8", "Safety Evaluation", safety))

        # Section 9: Discussion and Conclusions
        discussion = await self._generate_discussion(trial_data, efficacy_results, safety_data)
        sections.append(DocumentSection("9", "Discussion and Conclusions", discussion))

        document = RegulatoryDocument(
                      document_id=f"CSR-{trial_data.get('trial_id', 'UNKNOWN')}-{datetime.now().strftime('%Y%m%d')}",
                      document_type=DocumentType.CLINICAL_STUDY_REPORT,
                      title=f"Clinical Study Report: {trial_data.get('trial_name', 'Untitled Study')}",
                      version="1.0",
                      created_date=datetime.now(),
                      trial_id=trial_data.get('trial_id', ''),
                      sponsor=trial_data.get('sponsor', ''),
                      sections=sections,
                      compliance_region=RegulatoryRegion.FDA
        )

        self.generated_documents.append(document)
        return document

    async def _generate_synopsis(self, trial_data: Dict, results: Dict) -> str:
              """Generate study synopsis using Gemini."""
              prompt = f"""Generate a clinical study synopsis following ICH E3 guidelines:

      Study: {trial_data.get('trial_name')}
      Drug: {trial_data.get('drug_name')}
      Indication: {trial_data.get('indication')}
      Design: {trial_data.get('design', 'Randomized, double-blind')}
      Duration: {trial_data.get('duration', '12 weeks')}
      Sample Size: {trial_data.get('sample_size', 100)}
      Primary Endpoint: {trial_data.get('primary_endpoint')}

      Results Summary:
      {json.dumps(results, indent=2)}

      Write a professional 300-word synopsis covering objectives, methodology, results, and conclusions.
      """

        response = await self.model.generate_content_async(prompt)
        return response.text

    async def _generate_introduction(self, trial_data: Dict) -> str:
              """Generate introduction section."""
              prompt = f"""Write the Introduction section for a Clinical Study Report:

      Drug: {trial_data.get('drug_name')}
      Drug Class: {trial_data.get('drug_class')}
      Indication: {trial_data.get('indication')}
      Mechanism: {trial_data.get('mechanism', 'Not specified')}

      Include:
      1. Background on the disease/condition
      2. Rationale for the study drug
      3. Overview of nonclinical and prior clinical data
      4. Study rationale

      Write 200-300 words in formal regulatory language.
      """
              response = await self.model.generate_content_async(prompt)
              return response.text

    def _format_objectives(self, trial_data: Dict) -> str:
              """Format study objectives section."""
              primary = trial_data.get('primary_objective', 'Evaluate efficacy and safety')
              secondary = trial_data.get('secondary_objectives', [])

        content = f"**Primary Objective:**\\n{primary}\\n\\n"

        if secondary:
                      content += "**Secondary Objectives:**\\n"
                      for i, obj in enumerate(secondary, 1):
                                        content += f"{i}. {obj}\\n"

                  return content

    async def _generate_study_plan(self, trial_data: Dict) -> str:
              """Generate investigational plan section."""
              return f"""**Study Design:**
      {trial_data.get('design', 'Randomized, double-blind, placebo-controlled')}

      **Study Population:**
      - Target enrollment: {trial_data.get('sample_size', 100)} patients
      - Age range: {trial_data.get('age_range', '18-75 years')}
      - Key inclusion: {trial_data.get('indication')}

      **Treatment Groups:**
      - Active: {trial_data.get('drug_name')} {trial_data.get('dose', 'as prescribed')}
      - Control: Placebo or standard of care

      **Duration:**
      - Treatment period: {trial_data.get('duration', '12 weeks')}
      - Follow-up: {trial_data.get('follow_up', '4 weeks')}

      **Endpoints:**
      - Primary: {trial_data.get('primary_endpoint', 'Change from baseline')}
      - Secondary: Safety and tolerability
      """

    def _format_patient_summary(self, patients: List[Dict]) -> str:
              """Format patient demographics summary."""
              n = len(patients)
              if n == 0:
                            return "No patient data available."

              ages = [p.get('age', 0) for p in patients]
              avg_age = sum(ages) / n if n > 0 else 0

        content = f"""**Patient Disposition:**
        - Enrolled: {n}
        - Completed: {int(n * 0.85)}
        - Discontinued: {int(n * 0.15)}

        **Demographics:**
        - Mean age: {avg_age:.1f} years
        - Age range: {min(ages)} - {max(ages)} years

        **Baseline Characteristics:**
        Baseline characteristics were generally balanced across treatment groups.
        """
        return content

    async def _generate_efficacy_section(self, results: Dict) -> str:
              """Generate efficacy evaluation section using Gemini."""
              prompt = f"""Write the Efficacy Evaluation section for a CSR based on these results:

      {json.dumps(results, indent=2)}

      Include:
      1. Primary efficacy analysis
      2. Statistical methods used
      3. Results summary with confidence intervals
      4. Subgroup analyses if applicable

      Use formal regulatory language with appropriate statistical terminology.
      """
              response = await self.model.generate_content_async(prompt)
              return response.text

    async def _generate_safety_section(self, safety_data: Dict) -> str:
              """Generate safety evaluation section."""
              prompt = f"""Write the Safety Evaluation section for a Clinical Study Report:

      Safety Data:
      {json.dumps(safety_data, indent=2)}

      Include:
      1. Extent of exposure
      2. Adverse events summary (by SOC and preferred term)
      3. Serious adverse events
      4. Deaths and discontinuations due to AEs
      5. Laboratory findings
      6. Overall safety conclusions

      Follow ICH E3 format and FDA guidance.
      """
              response = await self.model.generate_content_async(prompt)
              return response.text

    async def _generate_discussion(
              self, trial_data: Dict, efficacy: Dict, safety: Dict
    ) -> str:
              """Generate discussion and conclusions."""
              prompt = f"""Write the Discussion and Conclusions section for a CSR:

      Study: {trial_data.get('trial_name')}
      Drug: {trial_data.get('drug_name')}
      Indication: {trial_data.get('indication')}

      Efficacy Summary: {json.dumps(efficacy, indent=2)}
      Safety Summary: {json.dumps(safety, indent=2)}

      Include:
      1. Interpretation of efficacy results
      2. Benefit-risk assessment
      3. Limitations of the study
      4. Conclusions and clinical implications

      Write 300-400 words in formal regulatory style.
      """
              response = await self.model.generate_content_async(prompt)
              return response.text

    async def generate_safety_update(
              self,
              trial_id: str,
              safety_events: List[Dict],
              reporting_period: str
    ) -> RegulatoryDocument:
              """Generate a periodic safety update report."""
              prompt = f"""Generate a Safety Update Report for FDA submission:

      Trial ID: {trial_id}
      Reporting Period: {reporting_period}
      Number of Events: {len(safety_events)}

      Events Summary:
      {json.dumps(safety_events[:10], indent=2)}  # First 10 for context

      Include standard PSUR/DSUR sections:
      1. Executive Summary
      2. Safety Evaluation
      3. Signal Detection
      4. Benefit-Risk Analysis
      5. Conclusions

      Use formal FDA-compliant language.
      """

        response = await self.model.generate_content_async(prompt)

        sections = [
                      DocumentSection("1", "Executive Summary", "See detailed analysis below."),
                      DocumentSection("2", "Safety Evaluation", response.text),
                      DocumentSection("3", "Conclusions", "Based on the data reviewed, the benefit-risk profile remains favorable.")
        ]

        document = RegulatoryDocument(
                      document_id=f"SUR-{trial_id}-{datetime.now().strftime('%Y%m%d')}",
                      document_type=DocumentType.SAFETY_UPDATE,
                      title=f"Safety Update Report - {trial_id}",
                      version="1.0",
                      created_date=datetime.now(),
                      trial_id=trial_id,
                      sponsor="",
                      sections=sections,
                      compliance_region=RegulatoryRegion.FDA
        )

        return document

    def get_document_summary(self) -> Dict[str, Any]:
              """Get summary of all generated documents."""
              return {
                  "total_documents": len(self.generated_documents),
                  "by_type": {
                      dt.value: sum(1 for d in self.generated_documents if d.document_type == dt)
                      for dt in DocumentType
                  },
                  "recent": [
                      {"id": d.document_id, "type": d.document_type.value, "date": d.created_date.isoformat()}
                      for d in self.generated_documents[-5:]
                  ]
              }
