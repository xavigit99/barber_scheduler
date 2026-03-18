from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from backend.infrastructure.database import Base


class ClinicalRecord(Base):
    """Health/allergy record for a client (F41 — Clinical Records)."""

    __tablename__ = "clinical_records"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    alergias = Column(Text, nullable=True)
    notas_saude = Column(Text, nullable=True)
    consentimento_assinado = Column(Boolean, nullable=False, default=False)
    consentimento_data = Column(DateTime, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)


class ClinicalNote(Base):
    """Individual clinical note attached to a client record (F41)."""

    __tablename__ = "clinical_notes"

    id = Column(Integer, primary_key=True, index=True)
    clinical_record_id = Column(
        Integer, ForeignKey("clinical_records.id"), nullable=False, index=True
    )
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    nota = Column(Text, nullable=False)
    criado_em = Column(DateTime, nullable=False)
    barber_id = Column(Integer, ForeignKey("barbeiros.id"), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
