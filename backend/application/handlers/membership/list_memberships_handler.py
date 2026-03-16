from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_memberships_query import ListMembershipsQuery
from backend.core.barbershop import Barbershop
from backend.core.barbershop_membership import BarbershopMembership
from backend.core.exceptions import NotFoundError
from repositories.base_repository import BaseRepository


class ListMembershipsHandler(RequestHandler[ListMembershipsQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListMembershipsQuery) -> list:
        if BaseRepository(Barbershop, self.db, tenant_id=query.tenant_id).get(query.barbershop_id) is None:
            raise NotFoundError("Barbershop not found")

        return (
            self.db.query(BarbershopMembership)
            .filter(
                BarbershopMembership.barbershop_id == query.barbershop_id,
                BarbershopMembership.tenant_id == query.tenant_id,
                BarbershopMembership.deleted.is_(False),
            )
            .all()
        )
