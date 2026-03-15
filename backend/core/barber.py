from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Barber(Base):
    __tablename__ = "barbeiros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
