from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_invoices_query import ListInvoicesQuery
from backend.core.invoice import Invoice
from repositories.base_repository import BaseRepository


class ListInvoicesHandler(RequestHandler[ListInvoicesQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListInvoicesQuery) -> list:
        repository = BaseRepository(Invoice, self.db, tenant_id=query.tenant_id)
        return repository.list()
