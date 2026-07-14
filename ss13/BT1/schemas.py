from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class MenuItemRequestDTO(BaseModel):
    dish_code: str
    dish_name: str = Field(min_length=1)
    calorie_count: int = Field(gt=0)
    price: float = Field(gt=0)
    status: str


class MenuItemUpdateDTO(BaseModel):
    dish_code: Optional[str] = None
    dish_name: Optional[str] = None
    calorie_count: Optional[int] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None


class MenuItemResponseDTO(BaseModel):
    id: int
    dish_code: str
    dish_name: str
    calorie_count: int
    price: float
    status: str

    model_config = ConfigDict(from_attributes=True)