from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.application.commands.add_clinical_note_command import (
    AddClinicalNoteCommand,
)
from backend.application.commands.sign_clinical_consent_command import (
    SignClinicalConsentCommand,
)
from backend.application.commands.upsert_clinical_record_command import (
    UpsertClinicalRecordCommand,
)
from backend.application.queries.get_clinical_record_query import (
    GetClinicalRecordQuery,
)
from backend.application.queries.list_clinical_notes_query import (
    ListClinicalNotesQuery,
)
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    ClinicalNoteCreate,
    ClinicalNoteResponse,
    ClinicalRecordResponse,
    ClinicalRecordUpsert,
)
from meditor import build_mediator

router = APIRouter(prefix="/clinical", tags=["Clinical Records"])


@router.get("/{client_id}", response_model=ClinicalRecordResponse | None)
async def get_clinical_record(
    client_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(
        GetClinicalRecordQuery(client_id=client_id, tenant_id=tenant_id)
    )


@router.put("/{client_id}", response_model=ClinicalRecordResponse)
async def upsert_clinical_record(
    client_id: int,
    payload: ClinicalRecordUpsert,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            UpsertClinicalRecordCommand(
                client_id=client_id,
                alergias=payload.alergias,
                notas_saude=payload.notas_saude,
                tenant_id=tenant_id,
            )
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.post(
    "/{client_id}/consent",
    response_model=ClinicalRecordResponse,
)
async def sign_consent(
    client_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            SignClinicalConsentCommand(client_id=client_id, tenant_id=tenant_id)
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.post(
    "/{client_id}/notes",
    response_model=ClinicalNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_clinical_note(
    client_id: int,
    payload: ClinicalNoteCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            AddClinicalNoteCommand(
                client_id=client_id,
                nota=payload.nota,
                tenant_id=tenant_id,
            )
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/{client_id}/notes",
    response_model=list[ClinicalNoteResponse],
)
async def list_clinical_notes(
    client_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(
        ListClinicalNotesQuery(client_id=client_id, tenant_id=tenant_id)
    )
