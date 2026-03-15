import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.api.routes.appointment_routes import router as appointment_router
from backend.api.routes.auth_routes import router as auth_router
from backend.api.routes.availability_routes import router as availability_router
from backend.api.routes.barber_routes import router as barber_router
from backend.api.routes.barbershop_routes import router as barbershop_router
from backend.api.routes.client_routes import router as client_router
from backend.api.routes.health_routes import router as health_router
from backend.api.routes.service_routes import router as service_router
from backend.core.logging_config import setup_logging
from backend.infrastructure.database import Base, engine

# ── Logging ─────────────────────────────────────────────────────────────────
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ── Database ─────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Rate limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Barber Scheduler API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
_origins = [o.strip() for o in _raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Security headers ──────────────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(barbershop_router)
app.include_router(barber_router)
app.include_router(client_router)
app.include_router(service_router)
app.include_router(availability_router)
app.include_router(appointment_router)

logger.info("Barber Scheduler API started", extra={"origins": _origins})
