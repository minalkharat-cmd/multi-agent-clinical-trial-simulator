"""
Enterprise Repository Pattern Implementation
Multi-Agent Clinical Trial Simulator

This module implements the Repository pattern for data access,
providing a clean abstraction over SQLAlchemy ORM with
21 CFR Part 11 compliant audit trail integration.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from datetime import datetime
from uuid import UUID
import hashlib
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .models import (
    Base, AuditLog, AuditAction, AuditMixin,
    ClinicalTrial, Patient, StudySite, Treatment,
    VitalSign, LabResult, AdverseEvent, DosingRecord,
    SimulationRun, ElectronicSignature
)

T = TypeVar('T', bound=Base)


# =============================================================================
# BASE REPOSITORY
# =============================================================================

class BaseRepository(ABC, Generic[T]):
      """
          Abstract base repository implementing common CRUD operations
              with full audit trail support for 21 CFR Part 11 compliance.
                  """

    def __init__(self, session: Session, user_id: str, user_name: str = None):
              """
                      Initialize repository with database session and user context.

                                      Args:
                                                  session: SQLAlchemy session
                                                              user_id: Current user's ID for audit trail
                                                                          user_name: Current user's name for audit trail
                                                                                  """
              self._session = session
              self._user_id = user_id
              self._user_name = user_name or user_id

    @property
    @abstractmethod
    def _model_class(self) -> Type[T]:
              """Return the model class this repository manages."""
              pass

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
              """Calculate SHA-256 hash of data for integrity verification."""
              serialized = json.dumps(data, sort_keys=True, default=str)
              return hashlib.sha256(serialized.encode()).hexdigest()

    def _create_audit_log(
              self,
              action: AuditAction,
              record_id: str,
              field_name: str = None,
              old_value: Any = None,
              new_value: Any = None,
              reason: str = None
    ) -> AuditLog:
              """Create an audit log entry for any data change."""
              return AuditLog(
                  table_name=self._model_class.__tablename__,
                  record_id=str(record_id),
                  field_name=field_name,
                  action=action,
                  old_value=str(old_value) if old_value is not None else None,
                  new_value=str(new_value) if new_value is not None else None,
                  user_id=self._user_id,
                  user_name=self._user_name,
                  reason=reason,
                  timestamp=datetime.utcnow()
              )

    def create(self, entity: T, reason: str = "Initial creation") -> T:
              """
                      Create a new entity with audit trail.

                                      Args:
                                                  entity: Entity to create
                                                              reason: Reason for creation (required for 21 CFR Part 11)

                                                                                  Returns:
                                                                                              Created entity with ID
                                                                                                      """
              try:
                            # Set audit fields if entity supports them
                            if hasattr(entity, 'created_by'):
                                              entity.created_by = self._user_id
                                          if hasattr(entity, 'created_at'):
                                                            entity.created_at = datetime.utcnow()

                            self._session.add(entity)
                            self._session.flush()  # Get the ID without committing

            # Create audit log
                  audit_log = self._create_audit_log(
                                    action=AuditAction.CREATE,
                                    record_id=entity.id,
                                    reason=reason
                  )
            self._session.add(audit_log)

            return entity

except IntegrityError as e:
            self._session.rollback()
            raise ValueError(f"Integrity error creating entity: {str(e)}")
except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database error creating entity: {str(e)}")

    def get_by_id(self, entity_id: UUID, include_deleted: bool = False) -> Optional[T]:
              """
                      Retrieve an entity by its ID.

                                      Args:
                                                  entity_id: UUID of the entity
                                                              include_deleted: Whether to include soft-deleted entities

                                                                                  Returns:
                                                                                              Entity or None if not found
                                                                                                      """
              query = self._session.query(self._model_class).filter(
                  self._model_class.id == entity_id
              )

        # Check for soft delete if applicable
              if not include_deleted and hasattr(self._model_class, 'is_deleted'):
                            query = query.filter(self._model_class.is_deleted == False)

        return query.first()

    def get_all(
              self,
              skip: int = 0,
              limit: int = 100,
              order_by: str = None,
              descending: bool = False
    ) -> List[T]:
              """
                      Retrieve all entities with pagination.

                                      Args:
                                                  skip: Number of records to skip
                                                              limit: Maximum number of records to return
                                                                          order_by: Field name to order by
                                                                                      descending: Whether to order descending

                                                                                                          Returns:
                                                                                                                      List of entities
                                                                                                                              """
              query = self._session.query(self._model_class)

        # Check for soft delete if applicable
              if hasattr(self._model_class, 'is_deleted'):
                            query = query.filter(self._model_class.is_deleted == False)

        # Apply ordering
        if order_by and hasattr(self._model_class, order_by):
                      order_field = getattr(self._model_class, order_by)
                      query = query.order_by(desc(order_field) if descending else asc(order_field))

        return query.offset(skip).limit(limit).all()

    def update(
              self,
              entity_id: UUID,
              updates: Dict[str, Any],
              reason: str
    ) -> Optional[T]:
              """
                      Update an entity with audit trail.

                                      Args:
                                                  entity_id: UUID of entity to update
                                                              updates: Dictionary of field names and new values
                                                                          reason: Reason for update (required for 21 CFR Part 11)

                                                                                              Returns:
                                                                                                          Updated entity or None if not found
                                                                                                                  """
              entity = self.get_by_id(entity_id)
              if not entity:
                            return None

              # Check if entity is locked
              if hasattr(entity, 'is_locked') and entity.is_locked:
                            raise PermissionError("Cannot update locked entity")

        try:
                      for field_name, new_value in updates.items():
                                        if hasattr(entity, field_name):
                                                              old_value = getattr(entity, field_name)
                                                              setattr(entity, field_name, new_value)

                    # Create audit log for each field change
                              audit_log = self._create_audit_log(
                                                        action=AuditAction.UPDATE,
                                                        record_id=entity_id,
                                                        field_name=field_name,
                                                        old_value=old_value,
                                                        new_value=new_value,
                                                        reason=reason
                              )
                    self._session.add(audit_log)

            # Update audit fields
            if hasattr(entity, 'updated_by'):
                              entity.updated_by = self._user_id
                          if hasattr(entity, 'updated_at'):
                                            entity.updated_at = datetime.utcnow()
                                        if hasattr(entity, 'version'):
                                                          entity.version += 1

            return entity

except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database error updating entity: {str(e)}")

    def delete(self, entity_id: UUID, reason: str, hard_delete: bool = False) -> bool:
              """
                      Delete an entity (soft delete by default).

                                      Args:
                                                  entity_id: UUID of entity to delete
                                                              reason: Reason for deletion (required for 21 CFR Part 11)
                                                                          hard_delete: Whether to permanently delete (use with caution)

                                                                                              Returns:
                                                                                                          True if deleted, False if not found
                                                                                                                  """
              entity = self.get_by_id(entity_id, include_deleted=True)
              if not entity:
                            return False

              # Check if entity is locked
              if hasattr(entity, 'is_locked') and entity.is_locked:
                            raise PermissionError("Cannot delete locked entity")

        try:
                      if hard_delete:
                                        # Hard delete - actually remove from database
                                        self._session.delete(entity)
        else:
                # Soft delete - mark as deleted
                          if hasattr(entity, 'is_deleted'):
                                                entity.is_deleted = True
                                                entity.deleted_at = datetime.utcnow()
                                                entity.deleted_by = self._user_id
        else:
                    # If no soft delete support, do hard delete
                              self._session.delete(entity)

            # Create audit log
                      audit_log = self._create_audit_log(
                                        action=AuditAction.DELETE,
                                        record_id=entity_id,
                                        reason=reason
                      )
            self._session.add(audit_log)

            return True

except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database error deleting entity: {str(e)}")

    def lock(self, entity_id: UUID, reason: str) -> Optional[T]:
              """Lock an entity to prevent further modifications."""
              entity = self.get_by_id(entity_id)
              if not entity or not hasattr(entity, 'is_locked'):
                            return None

              entity.is_locked = True
              entity.locked_at = datetime.utcnow()
              entity.locked_by = self._user_id

        audit_log = self._create_audit_log(
                      action=AuditAction.LOCK,
                      record_id=entity_id,
                      reason=reason
        )
        self._session.add(audit_log)

        return entity

    def unlock(self, entity_id: UUID, reason: str) -> Optional[T]:
              """Unlock a previously locked entity."""
              entity = self.get_by_id(entity_id)
              if not entity or not hasattr(entity, 'is_locked'):
                            return None

              entity.is_locked = False
              entity.locked_at = None
              entity.locked_by = None

        audit_log = self._create_audit_log(
                      action=AuditAction.UNLOCK,
                      record_id=entity_id,
                      reason=reason
        )
        self._session.add(audit_log)

        return entity

    def count(self, filters: Dict[str, Any] = None) -> int:
              """Count entities matching optional filters."""
              query = self._session.query(func.count(self._model_class.id))

        if hasattr(self._model_class, 'is_deleted'):
                      query = query.filter(self._model_class.is_deleted == False)

        if filters:
                      for field, value in filters.items():
                                        if hasattr(self._model_class, field):
                                                              query = query.filter(getattr(self._model_class, field) == value)

                                return query.scalar()

    def exists(self, entity_id: UUID) -> bool:
              """Check if an entity exists."""
        return self.get_by_id(entity_id) is not None

    def commit(self):
              """Commit current transaction."""
        try:
                      self._session.commit()
except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Database commit error: {str(e)}")

    def rollback(self):
              """Rollback current transaction."""
        self._session.rollback()


# =============================================================================
# SPECIALIZED REPOSITORIES
# =============================================================================

class ClinicalTrialRepository(BaseRepository[ClinicalTrial]):
      """Repository for Clinical Trial entities."""

    @property
    def _model_class(self) -> Type[ClinicalTrial]:
              return ClinicalTrial

    def get_by_protocol(self, protocol_number: str) -> Optional[ClinicalTrial]:
              """Get trial by protocol number."""
        return self._session.query(ClinicalTrial).filter(
                      ClinicalTrial.protocol_number == protocol_number
        ).first()

    def get_by_nct(self, nct_number: str) -> Optional[ClinicalTrial]:
              """Get trial by NCT number (ClinicalTrials.gov)."""
        return self._session.query(ClinicalTrial).filter(
                      ClinicalTrial.nct_number == nct_number
        ).first()

    def get_active_trials(self, sponsor: str = None) -> List[ClinicalTrial]:
              """Get all active trials, optionally filtered by sponsor."""
        query = self._session.query(ClinicalTrial).filter(
                      ClinicalTrial.is_active == True
        )
        if sponsor:
                      query = query.filter(ClinicalTrial.sponsor == sponsor)
                  return query.all()

    def get_enrollment_summary(self, trial_id: UUID) -> Dict[str, int]:
              """Get enrollment summary for a trial."""
              trial = self.get_by_id(trial_id)
              if not trial:
                            return {}
                        return {
                                      "target": trial.target_enrollment or 0,
                                      "actual": trial.actual_enrollment or 0,
                                      "remaining": (trial.target_enrollment or 0) - (trial.actual_enrollment or 0)
                        }


class PatientRepository(BaseRepository[Patient]):
      """Repository for Patient entities."""

    @property
    def _model_class(self) -> Type[Patient]:
              return Patient

    def get_by_subject_id(self, trial_id: UUID, subject_id: str) -> Optional[Patient]:
              """Get patient by subject ID within a trial."""
        return self._session.query(Patient).filter(
                      and_(
                                        Patient.trial_id == trial_id,
                                        Patient.subject_id == subject_id
                      )
        ).first()

    def get_by_trial(
              self,
              trial_id: UUID,
              status: str = None,
              skip: int = 0,
              limit: int = 100
    ) -> List[Patient]:
              """Get all patients for a trial."""
        query = self._session.query(Patient).filter(Patient.trial_id == trial_id)
        if status:
                      query = query.filter(Patient.status == status)
                  return query.offset(skip).limit(limit).all()

    def get_by_site(self, site_id: UUID) -> List[Patient]:
              """Get all patients at a specific site."""
        return self._session.query(Patient).filter(
                      Patient.site_id == site_id
        ).all()

    def count_by_status(self, trial_id: UUID) -> Dict[str, int]:
              """Get patient counts by status for a trial."""
        results = self._session.query(
                      Patient.status,
                      func.count(Patient.id)
        ).filter(
                      Patient.trial_id == trial_id
        ).group_by(Patient.status).all()

        return {str(status): count for status, count in results}


class AdverseEventRepository(BaseRepository[AdverseEvent]):
      """Repository for Adverse Event entities."""

    @property
    def _model_class(self) -> Type[AdverseEvent]:
              return AdverseEvent

    def get_by_patient(
              self,
              patient_id: UUID,
              serious_only: bool = False
    ) -> List[AdverseEvent]:
              """Get all adverse events for a patient."""
        query = self._session.query(AdverseEvent).filter(
                      AdverseEvent.patient_id == patient_id
        )
        if serious_only:
                      query = query.filter(AdverseEvent.is_serious == True)
                  return query.order_by(desc(AdverseEvent.onset_date)).all()

    def get_serious_events(self, trial_id: UUID) -> List[AdverseEvent]:
              """Get all serious adverse events for a trial."""
              return self._session.query(AdverseEvent).join(Patient).filter(
                  and_(
                      Patient.trial_id == trial_id,
                      AdverseEvent.is_serious == True
                  )
              ).all()

    def get_by_severity(
              self,
              trial_id: UUID,
              severity: str
    ) -> List[AdverseEvent]:
              """Get adverse events by severity grade."""
              return self._session.query(AdverseEvent).join(Patient).filter(
                  and_(
                      Patient.trial_id == trial_id,
                      AdverseEvent.severity == severity
                  )
              ).all()

    def count_by_meddra_term(self, trial_id: UUID) -> Dict[str, int]:
              """Count adverse events by MedDRA preferred term."""
              results = self._session.query(
                  AdverseEvent.meddra_pt_term,
                  func.count(AdverseEvent.id)
              ).join(Patient).filter(
                  Patient.trial_id == trial_id
              ).group_by(AdverseEvent.meddra_pt_term).all()

        return {term or "Unknown": count for term, count in results}


class SimulationRunRepository(BaseRepository[SimulationRun]):
      """Repository for Simulation Run entities."""

    @property
    def _model_class(self) -> Type[SimulationRun]:
              return SimulationRun

    def get_by_trial(
              self,
              trial_id: UUID,
              run_type: str = None
    ) -> List[SimulationRun]:
              """Get all simulation runs for a trial."""
              query = self._session.query(SimulationRun).filter(
                  SimulationRun.trial_id == trial_id
              )
              if run_type:
                            query = query.filter(SimulationRun.run_type == run_type)
                        return query.order_by(desc(SimulationRun.created_at)).all()

    def get_latest(self, trial_id: UUID, run_type: str) -> Optional[SimulationRun]:
              """Get the most recent simulation run of a given type."""
        return self._session.query(SimulationRun).filter(
                      and_(
                                        SimulationRun.trial_id == trial_id,
                                        SimulationRun.run_type == run_type,
                                        SimulationRun.status == "completed"
                      )
        ).order_by(desc(SimulationRun.completed_at)).first()


# =============================================================================
# UNIT OF WORK
# =============================================================================

class UnitOfWork:
      """
          Unit of Work pattern implementation for transaction management.
              Ensures atomic operations across multiple repositories.
                  """

    def __init__(self, session: Session, user_id: str, user_name: str = None):
              self._session = session
        self._user_id = user_id
        self._user_name = user_name

        # Initialize repositories
        self.trials = ClinicalTrialRepository(session, user_id, user_name)
        self.patients = PatientRepository(session, user_id, user_name)
        self.adverse_events = AdverseEventRepository(session, user_id, user_name)
        self.simulations = SimulationRunRepository(session, user_id, user_name)

    def __enter__(self):
              return self

    def __exit__(self, exc_type, exc_val, exc_tb):
              if exc_type is not None:
                            self.rollback()
else:
            self.commit()

    def commit(self):
              """Commit all changes."""
        try:
                      self._session.commit()
except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Transaction commit failed: {str(e)}")

    def rollback(self):
              """Rollback all changes."""
        self._session.rollback()
