from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional, List
import re

class StudentBase(BaseModel):
    student_code: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$", description="Mã sinh viên duy nhất")
    first_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên đệm")
    last_name: str = Field(..., min_length=1, max_length=100, description="Tên sinh viên")
    date_of_birth: date = Field(..., description="Ngày tháng năm sinh (Định dạng YYYY-MM-DD)")
    gender: Optional[str] = Field(None, pattern=r"^(Male|Female|Other)$", description="Giới tính (Male, Female hoặc Other)")
    phone: Optional[str] = Field(None, description="Số điện thoại liên hệ")
    class_id: Optional[int] = Field(None, description="ID của lớp học được liên kết")

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        today = date.today()
        # Kiểm tra xem ngày sinh có ở trong quá khứ không
        if v >= today:
            raise ValueError("Ngày sinh phải bé hơn ngày hiện tại.")
        # Tính toán tuổi sinh viên (tối thiểu là 18 tuổi)
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Sinh viên phải từ 18 tuổi trở lên.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Kiểm tra định dạng số điện thoại chuẩn Việt Nam / quốc tế
        pattern = r"^\+?[0-9]{9,15}$"
        if not re.match(pattern, v):
            raise ValueError("Định dạng số điện thoại không hợp lệ. Phải gồm 9-15 chữ số, có thể bắt đầu bằng +.")
        return v

class StudentCreate(StudentBase):
    user_id: int = Field(..., description="ID của tài khoản người dùng được liên kết")

class StudentRegister(BaseModel):
    # Chi tiết tài khoản người dùng
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$", description="Tên tài khoản đăng nhập")
    email: EmailStr = Field(..., description="Địa chỉ email liên hệ")
    password: str = Field(..., min_length=6, max_length=100, description="Mật khẩu (tối thiểu 6 ký tự)")
    
    # Chi tiết hồ sơ sinh viên
    student_code: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$", description="Mã sinh viên duy nhất")
    first_name: str = Field(..., min_length=1, max_length=100, description="Họ và tên đệm")
    last_name: str = Field(..., min_length=1, max_length=100, description="Tên sinh viên")
    date_of_birth: date = Field(..., description="Ngày sinh (YYYY-MM-DD)")
    gender: Optional[str] = Field(None, pattern=r"^(Male|Female|Other)$", description="Giới tính (Male, Female, Other)")
    phone: Optional[str] = Field(None, description="Số điện thoại liên hệ")
    class_id: Optional[int] = Field(None, description="ID lớp học được liên kết")

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("Ngày sinh phải ở trong quá khứ.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r"^\+?[0-9]{9,15}$"
        if not re.match(pattern, v):
            raise ValueError("Định dạng số điện thoại không hợp lệ.")
        return v

class StudentUpdate(BaseModel):
    student_code: Optional[str] = Field(None, min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$", description="Cập nhật mã sinh viên")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Cập nhật họ tên đệm")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Cập nhật tên")
    date_of_birth: Optional[date] = Field(None, description="Cập nhật ngày sinh")
    gender: Optional[str] = Field(None, pattern=r"^(Male|Female|Other)$", description="Cập nhật giới tính")
    phone: Optional[str] = Field(None, description="Cập nhật số điện thoại")
    class_id: Optional[int] = Field(None, description="Cập nhật lớp học")

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        if v >= date.today():
            raise ValueError("Ngày sinh phải ở trong quá khứ.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r"^\+?[0-9]{9,15}$"
        if not re.match(pattern, v):
            raise ValueError("Định dạng số điện thoại không hợp lệ.")
        return v

class StudentResponse(StudentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Nhập thêm thông tin lớp học lồng nhau cho thông tin chi tiết
from app.schemas.class_room import ClassRoomResponse

class StudentDetailResponse(StudentResponse):
    classroom: Optional[ClassRoomResponse] = Field(None, description="Thông tin chi tiết về lớp học liên kết")
    
    class Config:
        from_attributes = True
