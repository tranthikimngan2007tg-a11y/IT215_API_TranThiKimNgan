from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ScoreBase(BaseModel):
    student_id: int = Field(..., gt=0, description="ID của sinh viên trong cơ sở dữ liệu")
    subject_name: str = Field(..., min_length=2, max_length=100, description="Tên môn học, ví dụ: Toán, Python")
    score_value: float = Field(..., ge=0.0, le=10.0, description="Giá trị điểm số, phải nằm trong khoảng từ 0.0 đến 10.0")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Hệ số trọng số của đầu điểm, từ 0.0 đến 1.0 (ví dụ: 0.2 cho giữa kỳ, 0.8 cho cuối kỳ)")
    remarks: Optional[str] = Field(None, max_length=255, description="Góp ý hoặc nhận xét của giảng viên")

class ScoreCreate(ScoreBase):
    pass

class ScoreUpdate(BaseModel):
    subject_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Cập nhật môn học")
    score_value: Optional[float] = Field(None, ge=0.0, le=10.0, description="Cập nhật điểm số")
    weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Cập nhật trọng số điểm")
    remarks: Optional[str] = Field(None, max_length=255, description="Cập nhật nhận xét")

class ScoreResponse(ScoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Các schema phản hồi chi tiết mở rộng
class StudentBrief(BaseModel):
    id: int
    student_code: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class ScoreDetailResponse(ScoreResponse):
    student: StudentBrief = Field(..., description="Thông tin tóm tắt của sinh viên sở hữu điểm số này")

    class Config:
        from_attributes = True
