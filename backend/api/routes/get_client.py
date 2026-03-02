from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.application.queries.get_clientes_query import GetClientesQuery
from backend.infrastructure.database import SessionLocal, get_db
from meditor  import build_mediator

router = APIRouter(prefix="/clientesget", tags=["Clientes"])

@router.get("/")
async def listar_clientes(db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    return await mediator.send(GetClientesQuery())