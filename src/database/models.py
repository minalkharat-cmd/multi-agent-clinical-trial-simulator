"""
Enterprise Database Models
Multi-Agent Clinical Trial Simulator
21 CFR Part 11 Compliant Data Models

This module defines SQLAlchemy ORM models for clinical trial data management
with full audit trail capabilities and regulatory compliance.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from uuid import uuid4
import hashlib

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Enum as SQLEnum, Index,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID, JSONB

Base = declarative_base()


# =============================================================================
# ENUMERATIONS
# =============================================================================

class TrialPhase(str, Enum):
      """Clinical trial phases per FDA guidelines."""
      PRECLINICAL = "preclinical"
      PHASE_1 = "phase_1"
      PHASE_1A = "phase_1a"
      PHASE_1B = "phase_1b"
      PHASE_2 = "phase_2"
      PHASE_2A = "phase_2a"
      PHASE_2B = "phase_2b"
      PHASE_3 = "phase_3"
      PHASE_3A = "phase_3a"
      PHASE_3B = "phase_3b"
      PHASE_4 = "phase_4"


class PatientStatus(str, Enum):
      """Patient enrollment and participation status."""
      SCREENING = "screening"
      ENROLLED = "enrolled"
      RANDOMIZED = "randomized"
      ON_TREATMENT = "on_treatment"
      COMPLETED = "completed"
      WITHDRAWN = "withdrawn"
      LOST_TO_FOLLOWUP = "lost_to_followup"
      DISCONTINUED = "discontinued"
      SCREEN_FAILURE = "screen_failure"


class AdverseEventSeverity(str, Enum):
      """CTCAE v5.0 severity grades."""
      GRADE_1_MILD = "grade_1"
      GRADE_2_MODERATE = "grade_2"
      GRADE_3_SEVERE = "grade_3"
      GRADE_4_LIFE_THREATENING = "grade_4"
      GRADE_5_DEATH = "grade_5"


class AuditAction(str, Enum):
      """Audit trail action types for 21 CFR Part 11 compliance."""
      CREATE = "create"
      UPDATE = "update"
      DELETE = "delete"
      VIEW = "view"
      EXPORT = "export"
      SIGN = "electronic_signature"
      LOCK = "lock"
      UNLOCK = "unlock"


# =============================================================================
# AUDIT TRAIL MIXIN (21 CFR Part 11)
# =============================================================================

class AuditMixin:
      """
          Mixin providing 21 CFR Part 11 compliant audit trail fields.
              Every table inheriting this mixin will have complete audit history.
                  """
      created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
      created_by = Column(String(256), nullable=False)
      updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
      updated_by = Column(String(256))
      is_locked = Column(Boolean, default=False)
      locked_at = Column(DateTime)
      locked_by = Column(String(256))
      version = Column(Integer, default=1, nullable=False)
      data_hash = Column(String(64))  # SHA-256 hash for integrity verification

    def calculate_hash(self, data: str) -> str:
              """Calculate SHA-256 hash for data integrity."""
              return hashlib.sha256(data.encode()).hexdigest()


# =============================================================================
# CORE MODELS
# =============================================================================

class ClinicalTrial(Base, AuditMixin):
      """
          Clinical Trial Master Record.
              Contains all trial-level configuration and metadata.
                  """
      __tablename__ = "clinical_trials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    protocol_number = Column(String(50), unique=True, nullable=False, index=True)
    trial_title = Column(String(500), nullable=False)
    sponsor = Column(String(256), nullable=False)
    phase = Column(SQLEnum(TrialPhase), nullable=False)

    # Regulatory identifiers
    ind_number = Column(String(50))  # IND number for FDA
    eudract_number = Column(String(50))  # EU Clinical Trials Register
    nct_number = Column(String(50), index=True)  # ClinicalTrials.gov identifier

    # Study design
    study_type = Column(String(100))  # interventional, observational
    randomization_method = Column(String(100))
    blinding = Column(String(50))  # open, single, double, triple
    control_type = Column(String(100))  # placebo, active, standard of care

    # Target enrollment
    target_enrollment = Column(Integer)
    actual_enrollment = Column(Integer, default=0)

    # Dates
    protocol_date = Column(DateTime)
    first_patient_in = Column(DateTime)
    last_patient_in = Column(DateTime)
    database_lock_date = Column(DateTime)

    # Configuration as JSONB for flexibility
    inclusion_criteria = Column(JSONB)
    exclusion_criteria = Column(JSONB)
    endpoints = Column(JSONB)

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    patients = relationship("Patient", back_populates="trial", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="trial", cascade="all, delete-orphan")
    sites = relationship("StudySite", back_populates="trial", cascade="all, delete-orphan")

    __table_args__ = (
              Index('idx_trial_sponsor_phase', 'sponsor', 'phase'),
              Index('idx_trial_active', 'is_active'),
    )


class Patient(Base, AuditMixin):
      """
          Patient/Subject Record.
              Digital twin representation with comprehensive clinical data.
                  """
      __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_id = Column(UUID(as_uuid=True), ForeignKey("clinical_trials.id"), nullable=False)
    site_id = Column(UUID(as_uuid=True), ForeignKey("study_sites.id"))

    # Identifiers (de-identified per HIPAA)
    subject_id = Column(String(50), nullable=False)  # Study-specific ID
    screening_id = Column(String(50))
    randomization_number = Column(String(50))

    # Demographics
    age = Column(Integer)
    sex = Column(String(10))
    race = Column(String(100))
    ethnicity = Column(String(100))
    weight_kg = Column(Float)
    height_cm = Column(Float)
    bmi = Column(Float)

    # Clinical status
    status = Column(SQLEnum(PatientStatus), default=PatientStatus.SCREENING)

    # Dates
    informed_consent_date = Column(DateTime)
    screening_date = Column(DateTime)
    randomization_date = Column(DateTime)
    first_dose_date = Column(DateTime)
    last_dose_date = Column(DateTime)
    last_visit_date = Column(DateTime)
    discontinuation_date = Column(DateTime)

    # Genomic profile (simplified)
    genomic_data = Column(JSONB)

    # Medical history
    medical_history = Column(JSONB)
    concomitant_medications = Column(JSONB)

    # Relationships
    trial = relationship("ClinicalTrial", back_populates="patients")
    site = relationship("StudySite", back_populates="patients")
    vital_signs = relationship("VitalSign", back_populates="patient", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="patient", cascade="all, delete-orphan")
    adverse_events = relationship("AdverseEvent", back_populates="patient", cascade="all, delete-orphan")
    dosing_records = relationship("DosingRecord", back_populates="patient", cascade="all, delete-orphan")

    __table_args__ = (
              UniqueConstraint('trial_id', 'subject_id', name='uq_patient_trial_subject'),
              Index('idx_patient_status', 'status'),
              Index('idx_patient_trial', 'trial_id'),
    )

    @hybrid_property
    def calculated_bmi(self) -> Optional[float]:
              """Calculate BMI from weight and height."""
              if self.weight_kg and self.height_cm:
                            return round(self.weight_kg / ((self.height_cm / 100) ** 2), 2)
                        return None


class StudySite(Base, AuditMixin):
      """Clinical trial study site information."""
    __tablename__ = "study_sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_id = Column(UUID(as_uuid=True), ForeignKey("clinical_trials.id"), nullable=False)

    site_number = Column(String(20), nullable=False)
    site_name = Column(String(256), nullable=False)
    principal_investigator = Column(String(256))
    country = Column(String(100))
    region = Column(String(100))

    # IRB/Ethics information
    irb_name = Column(String(256))
    irb_approval_date = Column(DateTime)
    irb_approval_number = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)
    activation_date = Column(DateTime)

    # Relationships
    trial = relationship("ClinicalTrial", back_populates="sites")
    patients = relationship("Patient", back_populates="site")

    __table_args__ = (
              UniqueConstraint('trial_id', 'site_number', name='uq_site_trial_number'),
    )


class Treatment(Base, AuditMixin):
      """Treatment arm/intervention definition."""
    __tablename__ = "treatments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_id = Column(UUID(as_uuid=True), ForeignKey("clinical_trials.id"), nullable=False)

    arm_name = Column(String(100), nullable=False)
    arm_code = Column(String(20))
    drug_name = Column(String(256), nullable=False)
    drug_code = Column(String(50))

    # Dosing
    dose = Column(Float)
    dose_unit = Column(String(50))
    route_of_administration = Column(String(100))
    frequency = Column(String(100))

    # PK/PD parameters
    pk_parameters = Column(JSONB)
    pd_parameters = Column(JSONB)

    # Drug interaction data
    known_interactions = Column(JSONB)

    # Relationships
    trial = relationship("ClinicalTrial", back_populates="treatments")
    dosing_records = relationship("DosingRecord", back_populates="treatment")


class VitalSign(Base, AuditMixin):
      """Patient vital signs measurements."""
    __tablename__ = "vital_signs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    visit_date = Column(DateTime, nullable=False)
    visit_name = Column(String(100))

    # Measurements
    systolic_bp = Column(Float)
    diastolic_bp = Column(Float)
    heart_rate = Column(Float)
    respiratory_rate = Column(Float)
    temperature_celsius = Column(Float)
    oxygen_saturation = Column(Float)
    weight_kg = Column(Float)

    # Relationships
    patient = relationship("Patient", back_populates="vital_signs")

    __table_args__ = (
              Index('idx_vitals_patient_date', 'patient_id', 'visit_date'),
    )


class LabResult(Base, AuditMixin):
      """Laboratory test results with reference ranges."""
    __tablename__ = "lab_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    visit_date = Column(DateTime, nullable=False)
    visit_name = Column(String(100))
    collection_date = Column(DateTime)

    # Test information
    test_code = Column(String(50), nullable=False)
    test_name = Column(String(256), nullable=False)
    loinc_code = Column(String(20))

    # Results
    result_value = Column(Float)
    result_text = Column(String(256))
    result_unit = Column(String(50))

    # Reference range
    reference_low = Column(Float)
    reference_high = Column(Float)

    # Flags
    is_abnormal = Column(Boolean, default=False)
    is_clinically_significant = Column(Boolean, default=False)

    # Relationships
    patient = relationship("Patient", back_populates="lab_results")

    __table_args__ = (
              Index('idx_lab_patient_date', 'patient_id', 'visit_date'),
              Index('idx_lab_test_code', 'test_code'),
    )


class AdverseEvent(Base, AuditMixin):
      """Adverse event reporting per ICH E2B guidelines."""
    __tablename__ = "adverse_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    # Event identification
    ae_number = Column(String(50), nullable=False)
    meddra_pt_code = Column(String(20))
    meddra_pt_term = Column(String(256))
    meddra_soc = Column(String(256))

    # Event details
    description = Column(Text, nullable=False)
    onset_date = Column(DateTime, nullable=False)
    resolution_date = Column(DateTime)
    duration_days = Column(Integer)

    # Severity and seriousness
    severity = Column(SQLEnum(AdverseEventSeverity), nullable=False)
    is_serious = Column(Boolean, default=False)
    serious_criteria = Column(JSONB)  # death, hospitalization, etc.

    # Causality
    causality_assessment = Column(String(100))
    is_drug_related = Column(Boolean)

    # Outcome
    outcome = Column(String(100))
    action_taken = Column(String(256))

    # Regulatory reporting
    is_reportable = Column(Boolean, default=False)
    report_date = Column(DateTime)
    report_number = Column(String(100))

    # Relationships
    patient = relationship("Patient", back_populates="adverse_events")

    __table_args__ = (
              Index('idx_ae_patient', 'patient_id'),
              Index('idx_ae_severity', 'severity'),
              Index('idx_ae_serious', 'is_serious'),
    )


class DosingRecord(Base, AuditMixin):
      """Drug administration and dosing records."""
    __tablename__ = "dosing_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    treatment_id = Column(UUID(as_uuid=True), ForeignKey("treatments.id"), nullable=False)

    # Dosing details
    dose_date = Column(DateTime, nullable=False)
    dose_number = Column(Integer)
    actual_dose = Column(Float, nullable=False)
    dose_unit = Column(String(50))

    # Modifications
    dose_modified = Column(Boolean, default=False)
    modification_reason = Column(String(256))

    # PK sampling
    pk_sample_collected = Column(Boolean, default=False)
    pk_sample_time = Column(DateTime)

    # Relationships
    patient = relationship("Patient", back_populates="dosing_records")
    treatment = relationship("Treatment", back_populates="dosing_records")

    __table_args__ = (
              Index('idx_dosing_patient_date', 'patient_id', 'dose_date'),
    )


# =============================================================================
# AUDIT TRAIL TABLE
# =============================================================================

class AuditLog(Base):
      """
          21 CFR Part 11 Compliant Audit Trail.
              Records all data changes with full traceability.
                  """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # What changed
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(50), nullable=False)
    field_name = Column(String(100))

    # Change details
    action = Column(SQLEnum(AuditAction), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)

    # Who and when
    user_id = Column(String(256), nullable=False)
    user_name = Column(String(256))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Context
    reason = Column(Text)  # Required for changes per 21 CFR Part 11
    ip_address = Column(String(50))
    session_id = Column(String(256))

    # Data integrity
    previous_hash = Column(String(64))
    current_hash = Column(String(64))

    __table_args__ = (
              Index('idx_audit_table_record', 'table_name', 'record_id'),
              Index('idx_audit_timestamp', 'timestamp'),
              Index('idx_audit_user', 'user_id'),
    )


# =============================================================================
# ELECTRONIC SIGNATURE (21 CFR Part 11)
# =============================================================================

class ElectronicSignature(Base):
      """
          Electronic signature records for 21 CFR Part 11 compliance.
              Captures legally binding signatures on clinical data.
                  """
    __tablename__ = "electronic_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # What was signed
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(50), nullable=False)

    # Signature details
    signer_user_id = Column(String(256), nullable=False)
    signer_name = Column(String(256), nullable=False)
    signer_title = Column(String(256))

    # Signature meaning
    signature_meaning = Column(String(100), nullable=False)  # approval, review, etc.
    signature_reason = Column(Text)

    # Timestamp
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Cryptographic verification
    data_hash = Column(String(64), nullable=False)  # Hash of signed data
    signature_hash = Column(String(64), nullable=False)  # Hash of signature event

    __table_args__ = (
              Index('idx_esig_table_record', 'table_name', 'record_id'),
              Index('idx_esig_signer', 'signer_user_id'),
    )


# =============================================================================
# SIMULATION RESULTS
# =============================================================================

class SimulationRun(Base, AuditMixin):
      """Records of simulation executions for reproducibility."""
    __tablename__ = "simulation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    trial_id = Column(UUID(as_uuid=True), ForeignKey("clinical_trials.id"), nullable=False)

    run_name = Column(String(256))
    run_type = Column(String(100))  # population, pk_pd, adverse_event, etc.

    # Parameters
    input_parameters = Column(JSONB, nullable=False)
    random_seed = Column(Integer)

    # Results
    output_summary = Column(JSONB)
    detailed_results_path = Column(String(500))  # Path to detailed results file

    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    # Status
    status = Column(String(50))  # pending, running, completed, failed
    error_message = Column(Text)

    __table_args__ = (
              Index('idx_sim_trial', 'trial_id'),
              Index('idx_sim_status', 'status'),
    )
