from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class ServicePack(Base):
    """Template de pack vendável (criado pelo admin)."""

    __tablename__ = "service_packs"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    service_id = Column(Integer, ForeignKey("servicos.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    n_sessoes = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)


class ClientPack(Base):
    """Pack comprado por um cliente específico."""

    __tablename__ = "client_packs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    service_pack_id = Column(Integer, ForeignKey("service_packs.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sessoes_restantes = Column(Integer, nullable=False)
    comprado_em = Column(DateTime, nullable=False)
    expira_em = Column(Date, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
