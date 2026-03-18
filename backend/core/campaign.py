from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.infrastructure.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body_template = Column(String, nullable=False)
    segment_filters = Column(String, nullable=False, default="{}")  # JSON string
    status = Column(String, nullable=False, default="draft", index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    criado_em = Column(DateTime, nullable=False)
    enviado_em = Column(DateTime, nullable=True)
    total_sent = Column(Integer, nullable=False, default=0)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
