from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_loyalty_account_query import GetLoyaltyAccountQuery
from backend.core.loyalty import LoyaltyAccount


class GetLoyaltyAccountHandler(RequestHandler[GetLoyaltyAccountQuery, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetLoyaltyAccountQuery):
        account = (
            self.db.query(LoyaltyAccount)
            .filter(
                LoyaltyAccount.client_id == query.client_id,
                LoyaltyAccount.tenant_id == query.tenant_id,
            )
            .first()
        )
        if account is None:
            # Auto-create account on first access
            account = LoyaltyAccount(
                client_id=query.client_id,
                tenant_id=query.tenant_id,
                pontos_total=0,
                pontos_disponiveis=0,
                updated_at=datetime.now(),
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
        return account
