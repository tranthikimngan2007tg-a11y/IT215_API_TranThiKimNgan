from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import BoardingSlot
from schemas import (
    BoardingSlotRequestDTO,
    BoardingSlotUpdateDTO
)


def create_boarding_slot(
    boarding_slot: BoardingSlotRequestDTO,
    db: Session
):
    try:
        check_slot = db.query(BoardingSlot).filter(
            BoardingSlot.slot_number == boarding_slot.slot_number
        ).first()

        if check_slot:
            return None

        new_slot = BoardingSlot(
            slot_number=boarding_slot.slot_number,
            room_size=boarding_slot.room_size,
            price_per_day=boarding_slot.price_per_day,
            status=boarding_slot.status
        )

        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)

        return new_slot

    except SQLAlchemyError as s:
        db.rollback()
        raise s


def get_all_boarding_slots(db: Session):
    return db.query(BoardingSlot).all()


def get_boarding_slot_by_id(
    slot_id: int,
    db: Session
):
    return db.query(BoardingSlot).filter(
        BoardingSlot.id == slot_id
    ).first()
def update_boarding_slot(
    slot_id: int,
    boarding_slot: BoardingSlotUpdateDTO,
    db: Session
):
    try:
        db_slot = db.query(BoardingSlot).filter(
            BoardingSlot.id == slot_id
        ).first()

        if not db_slot:
            return None

        update_data = boarding_slot.model_dump(exclude_unset=True)

        if "slot_number" in update_data:
            check_slot = db.query(BoardingSlot).filter(
                BoardingSlot.slot_number == update_data["slot_number"],
                BoardingSlot.id != slot_id
            ).first()

            if check_slot:
                return False

        for key, value in update_data.items():
            setattr(db_slot, key, value)

        db.commit()
        db.refresh(db_slot)

        return db_slot

    except SQLAlchemyError as s:
        db.rollback()
        raise s


def delete_boarding_slot(
    slot_id: int,
    db: Session
):
    try:
        db_slot = db.query(BoardingSlot).filter(
            BoardingSlot.id == slot_id
        ).first()

        if not db_slot:
            return None

        db.delete(db_slot)
        db.commit()

        return db_slot

    except SQLAlchemyError as s:
        db.rollback()
        raise s