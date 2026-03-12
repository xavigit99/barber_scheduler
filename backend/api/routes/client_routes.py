from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.application.commands.create_client_command import CreateClientCommand
from backend.application.commands.delete_client_command import DeleteClientCommand
from backend.application.commands.update_client_command import UpdateClientCommand
from backend.application.queries.get_client_query import GetClientQuery
from backend.application.queries.list_clients_query import ListClientsQuery
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import ClientCreate, ClientResponse, ClientUpdate
from meditor import build_mediator

router = APIRouter(prefix="/clients", tags=["Clients"])


def _raise_not_found(client):
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    command = CreateClientCommand(
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
    )
    return await mediator.send(command)


@router.get("/", response_model=list[ClientResponse])
async def list_clients(db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    return await mediator.send(ListClientsQuery())


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    client = await mediator.send(GetClientQuery(client_id=client_id))
    return _raise_not_found(client)


def _build_update_command(client_id: int, payload: ClientUpdate) -> UpdateClientCommand:
    return UpdateClientCommand(
        client_id=client_id,
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
    )


@router.put("/{client_id}", response_model=ClientResponse)
async def replace_client(
    client_id: int,
    payload: ClientCreate,
    db: Session = Depends(get_db),
):
    mediator = build_mediator(db)
    command = UpdateClientCommand(
        client_id=client_id,
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
    )
    client = await mediator.send(command)
    return _raise_not_found(client)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
):
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided",
        )

    mediator = build_mediator(db)
    client = await mediator.send(_build_update_command(client_id, payload))
    return _raise_not_found(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    deleted = await mediator.send(DeleteClientCommand(client_id=client_id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
