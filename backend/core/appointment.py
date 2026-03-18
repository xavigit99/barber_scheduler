from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbeiros.id"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("servicos.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    # F26 — Presence confirmation
    status = Column(String, nullable=False, default="pending", index=True)
    confirmation_token = Column(String, nullable=True, unique=True, index=True)
    confirmed_at = Column(DateTime, nullable=True)
    # F25 — Reminder tracking
    reminder_sent_at = Column(DateTime, nullable=True)
    # F27 — Group appointments
    group_id = Column(String, nullable=True, index=True)
    # F34 — Stripe payments
    payment_status = Column(
        String, nullable=False, default="not_required", index=True,
    )
