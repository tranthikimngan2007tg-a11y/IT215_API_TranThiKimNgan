from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import Base, engine, get_db
from response import APIResponse
from schemas import BoardingSlotRequestDTO, BoardingSlotUpdateDTO, BoardingSlotResponseDTO
import boarding_slot_services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pet Boarding Slots"
)


@app.post("/boarding-slots")
def create_boarding_slot(
    boarding_slot: BoardingSlotRequestDTO,
    request: Request,
    db: Session = Depends(get_db)
):
    slot = boarding_slot_services.create_boarding_slot(boarding_slot, db)

    if slot is None:
        return APIResponse(
            statusCode=400,
            message="Slot number already exists",
            error="Bad Request",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=201,
        message="Create boarding slot successfully",
        error=None,
        data=BoardingSlotResponseDTO.model_validate(slot),
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.get("/boarding-slots")
def get_all_boarding_slots(
    request: Request,
    db: Session = Depends(get_db)
):
    slots = boarding_slot_services.get_all_boarding_slots(db)

    return APIResponse(
        statusCode=200,
        message="Get all boarding slots successfully",
        error=None,
        data=[BoardingSlotResponseDTO.model_validate(slot) for slot in slots],
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.get("/boarding-slots/{slot_id}")
def get_boarding_slot(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    slot = boarding_slot_services.get_boarding_slot_by_id(slot_id, db)

    if not slot:
        return APIResponse(
            statusCode=404,
            message="Boarding slot not found",
            error="Not Found",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=200,
        message="Get boarding slot successfully",
        error=None,
        data=BoardingSlotResponseDTO.model_validate(slot),
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.put("/boarding-slots/{slot_id}")
def update_boarding_slot(
    slot_id: int,
    boarding_slot: BoardingSlotUpdateDTO,
    request: Request,
    db: Session = Depends(get_db)
):
    slot = boarding_slot_services.update_boarding_slot(
        slot_id,
        boarding_slot,
        db
    )

    if slot is None:
        return APIResponse(
            statusCode=404,
            message="Boarding slot not found",
            error="Not Found",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    if slot is False:
        return APIResponse(
            statusCode=400,
            message="Slot number already exists",
            error="Bad Request",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=200,
        message="Update boarding slot successfully",
        error=None,
        data=BoardingSlotResponseDTO.model_validate(slot),
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.delete("/boarding-slots/{slot_id}")
def delete_boarding_slot(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    slot = boarding_slot_services.delete_boarding_slot(
        slot_id,
        db
    )

    if not slot:
        return APIResponse(
            statusCode=404,
            message="Boarding slot not found",
            error="Not Found",
            data=None,
            path=request.url.path,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return APIResponse(
        statusCode=200,
        message="Delete boarding slot successfully",
        error=None,
        data=None,
        path=request.url.path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )