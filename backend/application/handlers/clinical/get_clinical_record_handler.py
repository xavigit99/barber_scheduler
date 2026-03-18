from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_clinical_record_query import GetClinicalRecordQuery
from backend.core.clinical import ClinicalRecord


class GetClinicalRecordHandler(RequestHandler[GetClinicalRecordQuery, object]):
    """Returns the clinical record for a client (F41)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetClinicalRecordQuery) -> ClinicalRecord | None:
        q = self.db.query(ClinicalRecord).filter(
            ClinicalRecord.client_id == query.client_id,
            ClinicalRecord.deleted.is_(False),
        )
        if query.tenant_id is not None:
            q = q.filter(ClinicalRecord.tenant_id == query.tenant_id)
        return q.first()
