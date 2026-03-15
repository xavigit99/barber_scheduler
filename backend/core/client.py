from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Client(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)


# Legacy alias kept to avoid breaking existing imports while the codebase is normalized.
Cliente = Client
