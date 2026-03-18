from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class RedeemLoyaltyCommand(Request):
    client_id: int
    pontos: int
    tenant_id: int | None = None
    descricao: str | None = None
