from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_service_packs_query import ListServicePacksQuery
from backend.core.service_pack import ServicePack


class ListServicePacksHandler(RequestHandler[ListServicePacksQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListServicePacksQuery) -> list:
        q = self.db.query(ServicePack).filter(ServicePack.deleted.is_(False))
        if query.tenant_id is not None:
            q = q.filter(ServicePack.tenant_id == query.tenant_id)
        return q.order_by(ServicePack.id).all()
