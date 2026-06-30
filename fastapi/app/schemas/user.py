from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$", description="Tên đăng nhập chỉ chứa chữ cái, số, dấu gạch dưới hoặc gạch ngang")
    email: EmailStr = Field(..., description="Địa chỉ thư điện tử")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Mật khẩu của tài khoản (tối thiểu 6 ký tự)")
    role: UserRole = Field(default=UserRole.STUDENT, description="Vai trò của người dùng (lecturer hoặc student)")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Cập nhật địa chỉ thư điện tử")
    role: Optional[UserRole] = Field(None, description="Cập nhật vai trò tài khoản")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động tài khoản")

class UserChangePassword(BaseModel):
    current_password: str = Field(..., description="Mật khẩu hiện tại")
    new_password: str = Field(..., min_length=6, max_length=100, description="Mật khẩu mới (tối thiểu 6 ký tự)")

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        # Cấu hình tương thích ngược cho Pydantic v2
