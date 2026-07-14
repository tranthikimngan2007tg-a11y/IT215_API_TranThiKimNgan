from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from BT1.database import Base, engine, get_db
from BT1.parking_dto import ParkingSlotRequestDTO, APIResponse
from BT1.parking_service import (create_parking_slot,get_all_parking_slots,get_parking_slot_by_id)
from BT1.model import ParkingSlotModel

app = FastAPI(title="Parking Lot Management API")

Base.metadata.create_all(bind=engine)


@app.post(
    "/parking-slots",
    response_model=APIResponse,
    tags=["Parking Slots"]
)
def add_parking_slot(
    request: Request,
    parking: ParkingSlotRequestDTO,
    db: Session = Depends(get_db)
):
    result = create_parking_slot(db, parking)

    return APIResponse(
        statusCode=201,
        message="Thêm vị trí đỗ xe thành công",
        error=None,
        data={
            "id": result.id,
            "slot_code": result.slot_code,
            "zone_name": result.zone_name,
            "max_weight": result.max_weight,
            "is_available": result.is_available
        },
        path=request.url.path,
        timestamp=datetime.now(timezone.utc)
    )


@app.get(
    "/parking-slots",
    response_model=APIResponse,
    tags=["Parking Slots"]
)
def get_parking_slots(
    request: Request,
    db: Session = Depends(get_db)
):
    result = get_all_parking_slots(db)

    data = []

    for item in result:
        data.append({
            "id": item.id,
            "slot_code": item.slot_code,
            "zone_name": item.zone_name,
            "max_weight": item.max_weight,
            "is_available": item.is_available
        })

    return APIResponse(
        statusCode=200,
        message="Lấy danh sách vị trí đỗ xe thành công",
        error=None,
        data=data,
        path=request.url.path,
        timestamp=datetime.now(timezone.utc)
    )


@app.get(
    "/parking-slots/{slot_id}",
    response_model=APIResponse,
    tags=["Parking Slots"]
)
def get_parking_slot(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    result = get_parking_slot_by_id(db, slot_id)

    return APIResponse(
        statusCode=200,
        message="Lấy chi tiết vị trí đỗ xe thành công",
        error=None,
        data={
            "id": result.id,
            "slot_code": result.slot_code,
            "zone_name": result.zone_name,
            "max_weight": result.max_weight,
            "is_available": result.is_available
        },
        path=request.url.path,
        timestamp=datetime.now(timezone.utc)
    )
