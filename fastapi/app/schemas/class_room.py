from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ClassRoomBase(BaseModel):
    class_code: str = Field(
        ..., 
        min_length=2, 
        max_length=20, 
        pattern=r"^[A-Z0-9_-]+$", 
        description="Mã lớp học viết hoa gồm chữ cái và số, ví dụ: JV2403"
    )
    name: str = Field(..., min_length=3, max_length=100, description="Tên lớp học đầy đủ")
    description: Optional[str] = Field(None, max_length=255, description="Mô tả chi tiết về lớp học")

class ClassRoomCreate(ClassRoomBase):
    pass

class ClassRoomUpdate(BaseModel):
    class_code: Optional[str] = Field(None, min_length=2, max_length=20, pattern=r"^[A-Z0-9_-]+$", description="Mã lớp học mới")
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Tên lớp học mới")
    description: Optional[str] = Field(None, max_length=255, description="Mô tả lớp học mới")

class ClassRoomResponse(ClassRoomBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        # Cho phép chuyển đổi dữ liệu từ SQLAlchemy Model sang Pydantic Model
