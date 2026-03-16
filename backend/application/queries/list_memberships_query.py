from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class ListMembershipsQuery(Request):
    barbershop_id: int
    tenant_id: int
