from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from backend.infrastructure.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False, unique=True, index=True)
    client_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    barber_id = Column(Integer, ForeignKey("barbeiros.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
