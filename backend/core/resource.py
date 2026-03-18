from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Resource(Base):
    """Physical resource (room, chair, equipment) that can be booked (F38)."""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # e.g. "sala", "cadeira", "equipamento"
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
