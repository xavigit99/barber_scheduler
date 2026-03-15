from fastapi import HTTPException, status


def ensure_resource_found(resource, detail: str):
    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
    return resource


def ensure_resource_deleted(deleted: bool, detail: str) -> None:
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


def ensure_payload_has_changes(payload, detail: str = "At least one field must be provided"):
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
    return payload
