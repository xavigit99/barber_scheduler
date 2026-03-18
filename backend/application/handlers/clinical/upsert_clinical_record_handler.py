from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.upsert_clinical_record_command import (
    UpsertClinicalRecordCommand,
)
from backend.core.clinical import ClinicalRecord


class UpsertClinicalRecordHandler(RequestHandler[UpsertClinicalRecordCommand, object]):
    """Creates or updates a clinical record for a client (F41)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: UpsertClinicalRecordCommand) -> ClinicalRecord:
        record = (
            self.db.query(ClinicalRecord)
            .filter(
                ClinicalRecord.client_id == command.client_id,
                ClinicalRecord.deleted.is_(False),
            )
            .first()
        )

        if record is None:
            record = ClinicalRecord(
                client_id=command.client_id,
                tenant_id=command.tenant_id,
                alergias=command.alergias,
                notas_saude=command.notas_saude,
            )
            self.db.add(record)
        else:
            if command.alergias is not None:
                record.alergias = command.alergias
            if command.notas_saude is not None:
                record.notas_saude = command.notas_saude

        self.db.commit()
        self.db.refresh(record)
        return record
