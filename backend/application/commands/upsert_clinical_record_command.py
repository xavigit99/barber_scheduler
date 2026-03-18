from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpsertClinicalRecordCommand(Request):
    client_id: int
    alergias: str | None = None
    notas_saude: str | None = None
    tenant_id: int | None = None
