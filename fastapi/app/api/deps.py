from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password
from app.models.user import User, UserRole
from app.crud import crud_user
from app.schemas.auth import TokenPayload

# Thiết lập lược đồ xác thực HTTP Bearer cho phép dán trực tiếp token JWT
reusable_oauth2 = HTTPBearer(auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token_creds: Optional[HTTPAuthorizationCredentials] = Depends(reusable_oauth2)
) -> User:
    """
    Lấy thông tin người dùng hiện tại từ token JWT được gửi kèm trong header yêu cầu.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác minh thông tin đăng nhập hoặc phiên làm việc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token_creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực tài khoản. Vui lòng đăng nhập để thực hiện hành động này.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = token_creds.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(sub=username, role=role)
    except JWTError:
        raise credentials_exception
        
    user = crud_user.get_user_by_username(db, username=token_data.sub)
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Đảm bảo người dùng hiện tại đang ở trạng thái hoạt động (active).
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tài khoản đã bị vô hiệu hóa."
        )
    return current_user

class RoleChecker:
    """
    Dependency kiểm tra vai trò người dùng (RBAC) để phân quyền truy cập.
    Ví dụ: current_user: User = Depends(RoleChecker(["lecturer"]))
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập tài nguyên này."
            )
        return current_user
