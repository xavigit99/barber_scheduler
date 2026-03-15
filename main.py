import backend.core
from fastapi import FastAPI
from backend.api.routes.appointment_routes import router as appointment_router
from backend.api.routes.auth_routes import router as auth_router
from backend.api.routes.availability_routes import router as availability_router
from backend.api.routes.barbershop_routes import router as barbershop_router
from backend.api.routes.barber_routes import router as barber_router
from backend.api.routes.client_routes import router as client_router
from backend.api.routes.get_client import router as clinte_router_get

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(cliente_router)
app.include_router(clinte_router_get)
