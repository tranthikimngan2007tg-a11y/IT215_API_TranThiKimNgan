from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class BoardingSlotRequestDTO(BaseModel):
    slot_number: str
    room_size: str
    price_per_day: float = Field(gt=0)
    status: str


class BoardingSlotUpdateDTO(BaseModel):
    slot_number: Optional[str] = None
    room_size: Optional[str] = None
    price_per_day: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None


class BoardingSlotResponseDTO(BaseModel):
    id: int
    slot_number: str
    room_size: str
    price_per_day: float
    status: str

    model_config = ConfigDict(from_attributes=True)