from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ParkingSlotRequestDTO(BaseModel):
    slot_code: str = Field(..., min_length=1, max_length=50)
    zone_name: str = Field(..., min_length=3, max_length=255)
    max_weight: int = Field(..., gt=0)
    is_available: bool = True


class APIResponse(BaseModel):
    statusCode: int
    message: str
    error: Optional[Any] = None
    data: Optional[Any] = None
    path: str
    timestamp: datetime