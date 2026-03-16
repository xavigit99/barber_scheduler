from backend.api.http_utils import ensure_resource_deleted, ensure_resource_found
from backend.application.commands.create_membership_command import CreateMembershipCommand
from backend.application.commands.delete_membership_command import DeleteMembershipCommand
from backend.application.queries.list_memberships_query import ListMembershipsQuery
from backend.infrastructure.schemas import MembershipCreate


def build_create_membership_command(
    barbershop_id: int,
    payload: MembershipCreate,
    *,
    tenant_id: int,
) -> CreateMembershipCommand:
    return CreateMembershipCommand(
        barber_id=payload.barber_id,
        barbershop_id=barbershop_id,
        role=payload.role,
        tenant_id=tenant_id,
    )


def build_delete_membership_command(
    barbershop_id: int,
    membership_id: int,
    *,
    tenant_id: int,
) -> DeleteMembershipCommand:
    return DeleteMembershipCommand(
        membership_id=membership_id,
        barbershop_id=barbershop_id,
        tenant_id=tenant_id,
    )


def build_list_memberships_query(barbershop_id: int, *, tenant_id: int) -> ListMembershipsQuery:
    return ListMembershipsQuery(barbershop_id=barbershop_id, tenant_id=tenant_id)


def ensure_membership_found(membership):
    return ensure_resource_found(membership, "Membership not found")


def ensure_membership_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Membership not found")
