from pydantic import Field, BaseModel, ConfigDict
from typing import Optional

class WarehouseCreate(BaseModel):
    warehouse_name : str = Field(...,min_length=5)
    location : str = Field(...,min_length=5)

class PackageResponse(BaseModel):
    package_code : str
    weight : float

class WarehouseDetailResponse(PackageResponse):
    warehouse_name : str
    location : str 
    packages : Optional[list[PackageResponse]]  = None
    model_config = ConfigDict(from_attributes=True)
    

class PackageUpdate(BaseModel):
    package_code : Optional[str] = None
    weight : Optional[float] = None

class WaybillResponse(BaseModel):
    tracking_number : str
    shipping_status :str
    model_config = ConfigDict(from_attributes=True)