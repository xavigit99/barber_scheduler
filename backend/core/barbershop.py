from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Barbershop(Base):
    __tablename__ = "barbershops"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, unique=True, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
