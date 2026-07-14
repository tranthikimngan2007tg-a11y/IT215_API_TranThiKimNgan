from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any, Literal

app = FastAPI(
    title="Logistics Management API"
)


class APIResponse(BaseModel):
    statusCode: int
    message: str
    data: Optional[Any] = None


carriers = [
    {
        "id": 1,
        "code": "GHN",
        "name": "Giao Hang Nhanh",
        "max_weight_capacity": 5000,
        "status": "ACTIVE"
    },
    {
        "id": 2,
        "code": "GHTK",
        "name": "Giao Hang Tiet Kiem",
        "max_weight_capacity": 3000,
        "status": "ACTIVE"
    },
    {
        "id": 3,
        "code": "VTP",
        "name": "Viettel Post",
        "max_weight_capacity": 10000,
        "status": "SUSPENDED"
    }
]

shipments = [
    {
        "id": 1,
        "carrier_id": 1,
        "order_reference": "ORD-2026-001",
        "total_weight": 4200,
        "dispatch_date": "2026-07-01",
        "shift": "MORNING"
    }
]


class CarrierCreate(BaseModel):
    code: str
    name: str = Field(min_length=3)
    max_weight_capacity: int = Field(gt=0)
    status: Literal["ACTIVE", "INACTIVE", "SUSPENDED"]

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value


class ShipmentCreate(BaseModel):
    carrier_id: int
    order_reference: str
    total_weight: int = Field(gt=0)
    dispatch_date: str
    shift: Literal["MORNING", "AFTERNOON", "NIGHT"]


def find_carrier(carrier_id: int):
    for carrier in carriers:
        if carrier["id"] == carrier_id:
            return carrier
    return None


@app.post("/carriers", response_model=APIResponse)
def create_carrier(carrier: CarrierCreate):

    if any(c["code"].lower() == carrier.code.lower() for c in carriers):
        raise HTTPException(
            status_code=400,
            detail="Carrier code already exists"
        )

    new_carrier = carrier.model_dump()
    new_carrier["id"] = max([c["id"] for c in carriers], default=0) + 1

    carriers.append(new_carrier)

    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Carrier created successfully",
        data=new_carrier
    )


@app.get("/carriers", response_model=APIResponse)
def get_carriers(
    keyword: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    min_weight: Optional[int] = Query(None)
):

    result = carriers

    if keyword:
        keyword = keyword.lower()
        result = [
            c for c in result
            if keyword in c["code"].lower()
            or keyword in c["name"].lower()
        ]

    if status_filter:
        result = [
            c for c in result
            if c["status"] == status_filter
        ]

    if min_weight is not None:
        result = [
            c for c in result
            if c["max_weight_capacity"] >= min_weight
        ]

    return APIResponse(
        statusCode=200,
        message="Success",
        data=result
    )


@app.get("/carriers/{carrier_id}", response_model=APIResponse)
def get_carrier(carrier_id: int):

    carrier = find_carrier(carrier_id)

    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Carrier not found"
        )

    return APIResponse(
        statusCode=200,
        message="Success",
        data=carrier
    )


@app.put("/carriers/{carrier_id}", response_model=APIResponse)
def update_carrier(carrier_id: int, carrier_update: CarrierCreate):

    carrier = find_carrier(carrier_id)

    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Carrier not found"
        )

    for c in carriers:
        if (
            c["id"] != carrier_id
            and c["code"].lower() == carrier_update.code.lower()
        ):
            raise HTTPException(
                status_code=400,
                detail="Carrier code already exists"
            )

    carrier.update(carrier_update.model_dump())

    return APIResponse(
        statusCode=200,
        message="Carrier updated successfully",
        data=carrier
    )


@app.delete("/carriers/{carrier_id}", response_model=APIResponse)
def delete_carrier(carrier_id: int):

    carrier = find_carrier(carrier_id)

    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Carrier not found"
        )

    carriers.remove(carrier)

    return APIResponse(
        statusCode=200,
        message="Carrier deleted successfully",
        data=carrier
    )


@app.post("/shipments", response_model=APIResponse)
def create_shipment(shipment: ShipmentCreate):

    carrier = find_carrier(shipment.carrier_id)

    if carrier is None:
        raise HTTPException(
            status_code=404,
            detail="Carrier not found"
        )

    if carrier["status"] != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Carrier is not active"
        )

    if shipment.total_weight > carrier["max_weight_capacity"]:
        raise HTTPException(
            status_code=400,
            detail="Shipment exceeds carrier capacity"
        )

    for s in shipments:
        if (
            s["carrier_id"] == shipment.carrier_id
            and s["dispatch_date"] == shipment.dispatch_date
            and s["shift"] == shipment.shift
        ):
            raise HTTPException(
                status_code=400,
                detail="Carrier already has a shipment in this date and shift"
            )

    new_shipment = shipment.model_dump()
    new_shipment["id"] = max([s["id"] for s in shipments], default=0) + 1

    shipments.append(new_shipment)

    return APIResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Shipment created successfully",
        data=new_shipment
    )


@app.get("/shipments", response_model=APIResponse)
def get_shipments():

    return APIResponse(
        statusCode=200,
        message="Success",
        data=shipments
    )