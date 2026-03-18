from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.redeem_loyalty_command import RedeemLoyaltyCommand
from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.loyalty import LoyaltyAccount, LoyaltyTransaction


class RedeemLoyaltyHandler(RequestHandler[RedeemLoyaltyCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: RedeemLoyaltyCommand):
        account = (
            self.db.query(LoyaltyAccount)
            .filter(
                LoyaltyAccount.client_id == command.client_id,
                LoyaltyAccount.tenant_id == command.tenant_id,
            )
            .first()
        )
        if account is None:
            raise NotFoundError("Loyalty account not found")

        if account.pontos_disponiveis < command.pontos:
            raise ConflictError(
                f"Insufficient points: {account.pontos_disponiveis} available, "
                f"{command.pontos} requested"
            )

        now = datetime.now()
        account.pontos_disponiveis -= command.pontos
        account.updated_at = now

        tx = LoyaltyTransaction(
            loyalty_account_id=account.id,
            pontos=-command.pontos,
            tipo="redeem",
            criado_em=now,
            descricao=command.descricao,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(account)
        return account
