from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from BT1.model import ParkingSlotModel
from BT1.parking_dto import ParkingSlotRequestDTO


def create_parking_slot(db: Session, parking: ParkingSlotRequestDTO):
    try:
        new_parking = ParkingSlotModel(
            slot_code=parking.slot_code,
            zone_name=parking.zone_name,
            max_weight=parking.max_weight,
            is_available=parking.is_available
        )

        db.add(new_parking)
        db.commit()
        db.refresh(new_parking)

        return new_parking

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Slot code already exists"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )


def get_all_parking_slots(db: Session):
    return db.query(ParkingSlotModel).all()


def get_parking_slot_by_id(db: Session, slot_id: int):
    parking = db.query(ParkingSlotModel).filter(
        ParkingSlotModel.id == slot_id
    ).first()

    if parking is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    return parking