from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    invoice_number = Column(String, nullable=False)
    invoice_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft", index=True)
    criado_em = Column(DateTime, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
