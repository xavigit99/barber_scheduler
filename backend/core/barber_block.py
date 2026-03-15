from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from backend.infrastructure.database import Base


class BarberBlock(Base):
    __tablename__ = "barber_blocks"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbeiros.id"), nullable=False, index=True)
    kind = Column(String, nullable=False, index=True)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    reason = Column(String, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
