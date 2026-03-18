from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class AddClinicalNoteCommand(Request):
    client_id: int
    nota: str
    barber_id: int | None = None
    tenant_id: int | None = None
