from sqlalchemy import Column, Integer, String

from backend.infrastructure.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True, index=True)
