from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Product(Base):
    """Product that may be consumed during a service (F37 — Stock Management)."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    stock_atual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=0)
    preco_unitario = Column(Float, nullable=False, default=0)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)


class ServiceProduct(Base):
    """Links a product to a service with the quantity consumed per execution (F37)."""

    __tablename__ = "service_products"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("servicos.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantidade = Column(Integer, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
