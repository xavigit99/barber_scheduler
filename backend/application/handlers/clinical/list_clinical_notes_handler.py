from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_clinical_notes_query import ListClinicalNotesQuery
from backend.core.clinical import ClinicalNote, ClinicalRecord


class ListClinicalNotesHandler(RequestHandler[ListClinicalNotesQuery, list]):
    """Lists clinical notes for a client (F41)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListClinicalNotesQuery) -> list[ClinicalNote]:
        # First find the record
        record = (
            self.db.query(ClinicalRecord)
            .filter(
                ClinicalRecord.client_id == query.client_id,
                ClinicalRecord.deleted.is_(False),
            )
            .first()
        )
        if record is None:
            return []

        q = self.db.query(ClinicalNote).filter(
            ClinicalNote.clinical_record_id == record.id,
            ClinicalNote.deleted.is_(False),
        )
        if query.tenant_id is not None:
            q = q.filter(ClinicalNote.tenant_id == query.tenant_id)
        return q.order_by(ClinicalNote.criado_em.desc()).all()
