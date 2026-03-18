from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_client_packs_query import ListClientPacksQuery
from backend.core.service_pack import ClientPack


class ListClientPacksHandler(RequestHandler[ListClientPacksQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListClientPacksQuery) -> list:
        q = self.db.query(ClientPack).filter(
            ClientPack.client_id == query.client_id,
            ClientPack.deleted.is_(False),
            ClientPack.sessoes_restantes > 0,
        )
        if query.tenant_id is not None:
            q = q.filter(ClientPack.tenant_id == query.tenant_id)
        return q.order_by(ClientPack.comprado_em.desc()).all()
