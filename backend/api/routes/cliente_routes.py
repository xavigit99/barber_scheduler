from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.infrastructure.database import SessionLocal
from backend.application.commands.create_cliente_command import CreateClienteCommand
from backend.application.handlers.create_cliente_handler import CreateClienteHandler
from backend.infrastructure.schemas import ClienteCreate
from meditor  import build_mediator

router = APIRouter(prefix="/clientes", tags=["Clientes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
async def create_client(data: ClienteCreate, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    command = CreateClienteCommand(**data.model_dump())
    return await mediator.send(command)