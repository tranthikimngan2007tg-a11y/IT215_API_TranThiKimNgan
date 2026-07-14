from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any, Literal
from datetime import date
import re

app = FastAPI(
    title="IT Asset Management"
)


class APIResponse(BaseModel):
    statusCode: int
    message: str
    data: Optional[Any] = None


assets = [
    {
        "id": 1,
        "serial_number": "SN-MAC-01",
        "model": "MacBook Pro M3",
        "stock_available": 5,
        "status": "READY"
    },
    {
        "id": 2,
        "serial_number": "SN-DELL-02",
        "model": "Dell UltraSharp 27",
        "stock_available": 10,
        "status": "READY"
    },
    {
        "id": 3,
        "serial_number": "SN-THINK-03",
        "model": "ThinkPad X1 Carbon",
        "stock_available": 0,
        "status": "REPAIRING"
    }
]

allocations = [
    {
        "id": 1,
        "asset_id": 1,
        "employee_email": "dev.nguyen@company.com",
        "allocated_quantity": 1,
        "start_date": "2026-07-01",
        "duration_months": 12
    }
]


class AssetCreate(BaseModel):
    serial_number: str
    model: str = Field(min_length=2, max_length=255)
    stock_available: int = Field(ge=0)
    status: Literal["READY", "ALLOCATED", "REPAIRING", "SCRAPPED"]

    @field_validator("serial_number")
    @classmethod
    def validate_serial(cls, value):
        if not value.strip():
            raise ValueError("Serial number cannot be empty")
        return value

    @field_validator("model")
    @classmethod
    def validate_model(cls, value):
        if not value.strip():
            raise ValueError("Model cannot be empty")
        return value


class AllocationCreate(BaseModel):
    asset_id: int
    employee_email: str
    allocated_quantity: int = Field(gt=0)
    start_date: date
    duration_months: int = Field(ge=1, le=12)

    @field_validator("employee_email")
    @classmethod
    def validate_email(cls, value):
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, value):
            raise ValueError("Invalid email format")
        return value


def get_asset_by_id(asset_id: int):
    for asset in assets:
        if asset["id"] == asset_id:
            return asset
    return None


def generate_asset_id():
    if not assets:
        return 1
    return max(asset["id"] for asset in assets) + 1


def generate_allocation_id():
    if not allocations:
        return 1
    return max(item["id"] for item in allocations) + 1


@app.post(
    "/assets",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED
)
def create_asset(asset: AssetCreate):

    if any(
        item["serial_number"].lower() == asset.serial_number.lower()
        for item in assets
    ):
        raise HTTPException(
            status_code=400,
            detail="Serial number already exists"
        )

    new_asset = asset.model_dump()
    new_asset["id"] = generate_asset_id()

    assets.append(new_asset)

    return APIResponse(
        statusCode=201,
        message="Asset created successfully",
        data=new_asset
    )


@app.get("/assets", response_model=APIResponse)
def get_assets(
    keyword: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    min_stock: Optional[int] = Query(None)
):

    result = assets

    if keyword:
        keyword = keyword.lower()
        result = [
            asset for asset in result
            if keyword in asset["serial_number"].lower()
            or keyword in asset["model"].lower()
        ]

    if status_filter:
        result = [
            asset for asset in result
            if asset["status"] == status_filter
        ]

    if min_stock is not None:
        result = [
            asset for asset in result
            if asset["stock_available"] >= min_stock
        ]

    return APIResponse(
        statusCode=200,
        message="Success",
        data=result
    )


@app.get("/assets/{asset_id}", response_model=APIResponse)
def get_asset(asset_id: int):

    asset = get_asset_by_id(asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    return APIResponse(
        statusCode=200,
        message="Success",
        data=asset
    )


@app.put("/assets/{asset_id}", response_model=APIResponse)
def update_asset(asset_id: int, asset_update: AssetCreate):

    asset = get_asset_by_id(asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    for item in assets:
        if (
            item["id"] != asset_id
            and item["serial_number"].lower() == asset_update.serial_number.lower()
        ):
            raise HTTPException(
                status_code=400,
                detail="Serial number already exists"
            )

    asset.update(asset_update.model_dump())

    return APIResponse(
        statusCode=200,
        message="Asset updated successfully",
        data=asset
    )


@app.delete("/assets/{asset_id}", response_model=APIResponse)
def delete_asset(asset_id: int):

    asset = get_asset_by_id(asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    assets.remove(asset)

    return APIResponse(
        statusCode=200,
        message="Asset deleted successfully",
        data=asset
    )
@app.post(
    "/allocations",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED
)
def create_allocation(allocation: AllocationCreate):

    asset = get_asset_by_id(allocation.asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    if asset["status"] != "READY":
        raise HTTPException(
            status_code=400,
            detail="Asset is not ready"
        )

    if allocation.allocated_quantity > asset["stock_available"]:
        raise HTTPException(
            status_code=400,
            detail="Allocated quantity exceeds available stock"
        )

    new_allocation = allocation.model_dump()
    new_allocation["id"] = generate_allocation_id()
    new_allocation["start_date"] = str(new_allocation["start_date"])

    allocations.append(new_allocation)

    asset["stock_available"] -= allocation.allocated_quantity

    if asset["stock_available"] == 0:
        asset["status"] = "ALLOCATED"

    return APIResponse(
        statusCode=201,
        message="Allocation created successfully",
        data=new_allocation
    )


@app.get("/allocations", response_model=APIResponse)
def get_allocations():

    return APIResponse(
        statusCode=200,
        message="Success",
        data=allocations
    )