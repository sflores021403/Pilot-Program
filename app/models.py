from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Hub(Base):
    __tablename__ = "hubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    equipment = relationship("Equipment", back_populates="hub")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)

    serial_number = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    equipment_type = Column(String, nullable=False)

    hub_id = Column(
        Integer,
        ForeignKey("hubs.id"),
        nullable=True,
    )

    is_deployed = Column(Boolean, default=False, nullable=False)

    deployment_location = Column(String, nullable=True)

    notes = Column(String, nullable=True)

    qr_code = Column(String, nullable=True)

    last_checked_by = Column(String, nullable=True)

    last_checked_date = Column(Date, nullable=True)

    hub = relationship("Hub", back_populates="equipment")

    movements = relationship(
        "EquipmentMovement",
        back_populates="equipment",
    )


class EquipmentMovement(Base):
    __tablename__ = "equipment_movements"

    id = Column(Integer, primary_key=True, index=True)

    equipment_id = Column(
        Integer,
        ForeignKey("equipment.id"),
        nullable=False,
    )

    from_location = Column(String, nullable=True)
    to_location = Column(String, nullable=True)

    action = Column(String, nullable=False)

    performed_by = Column(String, nullable=True)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    equipment = relationship(
        "Equipment",
        back_populates="movements",
    )