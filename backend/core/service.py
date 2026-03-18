from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Service(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    duracao_minutos = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    # F27 — Group/class capacity (default 1 = individual session)
    max_capacity = Column(Integer, nullable=False, default=1)
