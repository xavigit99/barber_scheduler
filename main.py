import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import backend.core  # noqa: F401 — registers all models on Base.metadata
from backend.api.routes.appointment_routes import router as appointment_router
from backend.api.routes.audit_routes import router as audit_router
from backend.api.routes.auth_routes import router as auth_router
from backend.api.routes.availability_routes import router as availability_router
from backend.api.routes.barber_routes import router as barber_router
from backend.api.routes.barbershop_routes import router as barbershop_router
from backend.api.routes.campaign_routes import router as campaign_router
from backend.api.routes.client_routes import router as client_router
from backend.api.routes.clinical_routes import router as clinical_router
from backend.api.routes.feedback_routes import router as feedback_router
from backend.api.routes.health_routes import router as health_router
from backend.api.routes.invoice_routes import router as invoice_router
from backend.api.routes.loyalty_routes import router as loyalty_router
from backend.api.routes.membership_routes import router as membership_router
from backend.api.routes.pack_routes import router as pack_router
from backend.api.routes.payment_routes import router as payment_router
from backend.api.routes.product_routes import router as product_router
from backend.api.routes.public_routes import router as public_router
from backend.api.routes.qr_routes import router as qr_router
from backend.api.routes.report_routes import router as report_router
from backend.api.routes.resource_routes import router as resource_router
from backend.api.routes.saft_routes import router as saft_router
from backend.api.routes.service_routes import router as service_router
from backend.api.routes.stats_routes import router as stats_router
from backend.api.routes.webhook_routes import router as webhook_router
from backend.api.routes.widget_routes import router as widget_router
from backend.core.logging_config import setup_logging
from backend.core.notifications import build_notification_service, set_notification_service
from backend.infrastructure.database import Base, SessionLocal, engine
from backend.infrastructure.schema_guard import validate_database_schema

# ── Logging ─────────────────────────────────────────────────────────────────
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ── Notifications ─────────────────────────────────────────────────────────────
set_notification_service(build_notification_service())

# ── Database ──────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)
validate_database_schema(engine)

# ── Rate limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ── Scheduled jobs ────────────────────────────────────────────────────────────
def _run_reminders() -> None:
    from backend.core.reminders import send_appointment_reminders

    db = SessionLocal()
    try:
        send_appointment_reminders(db)
    finally:
        db.close()


def _run_birthdays() -> None:
    from backend.core.birthdays import send_birthday_messages

    db = SessionLocal()
    try:
        send_birthday_messages(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    reminder_interval = int(os.getenv("REMINDER_CHECK_INTERVAL_MINUTES", "30"))
    scheduler.add_job(_run_reminders, "interval", minutes=reminder_interval)
    scheduler.add_job(_run_birthdays, "cron", hour=9, minute=0)
    scheduler.start()
    logger.info(
        "Scheduler started (reminders every %dm, birthdays at 09:00)",
        reminder_interval,
    )
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Barber Scheduler API", lifespan=lifespan)
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
app.include_router(membership_router)
app.include_router(barber_router)
app.include_router(client_router)
app.include_router(service_router)
app.include_router(availability_router)
app.include_router(appointment_router)
app.include_router(public_router)
app.include_router(report_router)
app.include_router(audit_router)
app.include_router(stats_router)
app.include_router(feedback_router)
app.include_router(webhook_router)
app.include_router(pack_router)
app.include_router(loyalty_router)
app.include_router(campaign_router)
app.include_router(payment_router)
app.include_router(invoice_router)
app.include_router(saft_router)
app.include_router(product_router)
app.include_router(resource_router)
app.include_router(qr_router)
app.include_router(widget_router)
app.include_router(clinical_router)

logger.info("Barber Scheduler API started", extra={"origins": _origins})
