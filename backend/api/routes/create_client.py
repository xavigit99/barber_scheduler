from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.infrastructure.database import SessionLocal ,get_db
from backend.application.commands.create_cliente_command import CreateClienteCommand
from backend.infrastructure.schemas import ClienteCreate
from meditor  import build_mediator

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/")
async def create_client(data: ClienteCreate, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    command = CreateClienteCommand(**data.model_dump())
    return await mediator.send(command)