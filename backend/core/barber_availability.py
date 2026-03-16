from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, Time

from backend.infrastructure.database import Base


class BarberAvailability(Base):
    __tablename__ = "barber_availabilities"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="ck_barber_availability_weekday"),
    )

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbeiros.id"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
