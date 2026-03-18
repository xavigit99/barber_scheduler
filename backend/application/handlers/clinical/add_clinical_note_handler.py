from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.add_clinical_note_command import AddClinicalNoteCommand
from backend.core.clinical import ClinicalNote, ClinicalRecord


class AddClinicalNoteHandler(RequestHandler[AddClinicalNoteCommand, object]):
    """Adds a clinical note to a client's record (F41)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: AddClinicalNoteCommand) -> ClinicalNote:
        record = (
            self.db.query(ClinicalRecord)
            .filter(
                ClinicalRecord.client_id == command.client_id,
                ClinicalRecord.deleted.is_(False),
            )
            .first()
        )
        if record is None:
            # Auto-create record when adding first note
            record = ClinicalRecord(
                client_id=command.client_id,
                tenant_id=command.tenant_id,
            )
            self.db.add(record)
            self.db.flush()

        note = ClinicalNote(
            clinical_record_id=record.id,
            tenant_id=command.tenant_id,
            nota=command.nota,
            criado_em=datetime.now(UTC),
            barber_id=command.barber_id,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note
