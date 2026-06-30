from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token: str = Field(..., description="Token truy cập JWT")
    token_type: str = Field(..., description="Loại token (mặc định là bearer)")
    role: str = Field(..., description="Vai trò của người dùng được phân quyền")

class TokenPayload(BaseModel):
    sub: Optional[str] = Field(None, description="Tên đăng nhập (chủ thể token)")
    role: Optional[str] = Field(None, description="Vai trò tài khoản")

class LoginRequest(BaseModel):
    username: str = Field(..., description="Tên đăng nhập hoặc địa chỉ email")
    password: str = Field(..., description="Mật khẩu tài khoản")
