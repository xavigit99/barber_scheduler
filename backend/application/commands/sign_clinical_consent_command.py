from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class SignClinicalConsentCommand(Request):
    client_id: int
    tenant_id: int | None = None
