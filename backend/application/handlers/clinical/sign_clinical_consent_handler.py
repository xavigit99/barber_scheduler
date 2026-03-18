from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.sign_clinical_consent_command import (
    SignClinicalConsentCommand,
)
from backend.core.clinical import ClinicalRecord


class SignClinicalConsentHandler(RequestHandler[SignClinicalConsentCommand, object]):
    """Marks clinical consent as signed for a client (F41)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: SignClinicalConsentCommand) -> ClinicalRecord:
        record = (
            self.db.query(ClinicalRecord)
            .filter(
                ClinicalRecord.client_id == command.client_id,
                ClinicalRecord.deleted.is_(False),
            )
            .first()
        )
        if record is None:
            # Auto-create record on consent signature
            record = ClinicalRecord(
                client_id=command.client_id,
                tenant_id=command.tenant_id,
            )
            self.db.add(record)
            self.db.flush()

        record.consentimento_assinado = True
        record.consentimento_data = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(record)
        return record
