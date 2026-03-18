from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class LoyaltyAccount(Base):
    """Conta de pontos de fidelização de um cliente num tenant."""

    __tablename__ = "loyalty_accounts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    pontos_total = Column(Integer, nullable=False, default=0)
    pontos_disponiveis = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False)


class LoyaltyTransaction(Base):
    """Registo de ganho ou resgate de pontos."""

    __tablename__ = "loyalty_transactions"

    id = Column(Integer, primary_key=True, index=True)
    loyalty_account_id = Column(
        Integer, ForeignKey("loyalty_accounts.id"), nullable=False, index=True
    )
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    pontos = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)  # "earn" | "redeem"
    criado_em = Column(DateTime, nullable=False)
    descricao = Column(String, nullable=True)
