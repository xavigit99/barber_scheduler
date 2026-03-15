import backend.core
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.appointment_routes import router as appointment_router
from backend.api.routes.auth_routes import router as auth_router
from backend.api.routes.availability_routes import router as availability_router
from backend.api.routes.barbershop_routes import router as barbershop_router
from backend.api.routes.barber_routes import router as barber_router
from backend.api.routes.client_routes import router as client_router
from backend.api.routes.service_routes import router as service_router
from backend.api.routes.health_routes import router as health_router
from backend.infrastructure.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Barber Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(barbershop_router)
app.include_router(barber_router)
app.include_router(client_router)
app.include_router(service_router)
app.include_router(availability_router)
app.include_router(appointment_router)
