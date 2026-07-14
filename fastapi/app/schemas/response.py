from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class MetaResponse(BaseModel):
    currentPage: int = Field(..., description="Trang hiện tại (1-indexed)")
    pageSize: int = Field(..., description="Số lượng bản ghi trên một trang")
    totalPage: int = Field(..., description="Tổng số trang")
    totalRecord: int = Field(..., description="Tổng số lượng bản ghi thỏa mãn điều kiện")

class APIResponse(BaseModel, Generic[T]):
    statusCode: int = Field(..., description="Mã trạng thái HTTP phản hồi")
    message: str = Field(..., description="Thông điệp phản hồi bằng tiếng Việt")
    data: Optional[T] = Field(None, description="Dữ liệu chính trả về")
    error: Optional[Any] = Field(None, description="Chi tiết lỗi nếu có")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời điểm gửi phản hồi")
    meta: Optional[MetaResponse] = Field(None, description="Thông tin phân trang (chỉ áp dụng cho API tìm kiếm/phân trang/lọc)")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
