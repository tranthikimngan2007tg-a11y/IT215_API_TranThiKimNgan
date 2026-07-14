from sqlalchemy import Column, Integer, String, Boolean
from BT1.database import Base


class ParkingSlotModel(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    slot_code = Column(
        String(50),
        nullable=False,
        unique=True
    )

    zone_name = Column(
        String(255),
        nullable=False
    )

    max_weight = Column(
        Integer,
        nullable=False
    )

    is_available = Column(
        Boolean,
        nullable=False,
        default=True
    )