from fastapi import HTTPException, status


TENANT_HEADER_ALIAS = "X-Tenant-Id"


def require_tenant_id(tenant_id: int | None) -> int:
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id header is required",
        )
    return tenant_id
