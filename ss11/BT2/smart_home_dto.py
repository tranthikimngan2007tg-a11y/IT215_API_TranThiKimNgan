from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class SmartHomePlanRequestDTO(BaseModel):
    plan_code: str = Field(..., min_length=1, max_length=50)
    plan_name: str = Field(..., min_length=1, max_length=255)
    device_quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class APIResponse(BaseModel):
    statusCode: int
    message: str
    error: Optional[Any] = None
    data: Optional[Any] = None
    path: str
    timestamp: datetime