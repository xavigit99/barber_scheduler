from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from backend.infrastructure.database import Base


class BarbershopMembership(Base):
    __tablename__ = "barbershop_memberships"
    __table_args__ = (
        UniqueConstraint("barber_id", "barbershop_id", name="uq_membership_barber_barbershop"),
    )

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbeiros.id"), nullable=False, index=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    role = Column(String, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
