from fastapi import FastAPI
from backend.infrastructure.database import engine, Base
from backend.core.client import Cliente
from backend.api.routes.cliente_routes import router as cliente_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# registra rotas
app.include_router(cliente_router)