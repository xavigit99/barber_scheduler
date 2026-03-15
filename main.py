from fastapi import FastAPI
from backend.infrastructure.database import engine, Base
from backend.api.routes.create_client import router as cliente_router
from backend.api.routes.get_client import router as clinte_router_get

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(cliente_router)
app.include_router(clinte_router_get)
