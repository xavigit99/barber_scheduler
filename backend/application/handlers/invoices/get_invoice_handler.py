from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_invoice_query import GetInvoiceQuery
from backend.core.invoice import Invoice
from repositories.base_repository import BaseRepository


class GetInvoiceHandler(RequestHandler[GetInvoiceQuery, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetInvoiceQuery) -> Invoice | None:
        repository = BaseRepository(Invoice, self.db, tenant_id=query.tenant_id)
        return repository.get(query.invoice_id)
