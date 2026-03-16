from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class DeleteMembershipCommand(Request):
    membership_id: int
    barbershop_id: int
    tenant_id: int
