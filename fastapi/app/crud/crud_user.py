from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Lấy thông tin người dùng theo ID tài khoản
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Lấy thông tin người dùng dựa trên tên đăng nhập (username)
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Lấy thông tin người dùng dựa trên email đăng ký
    """
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Lấy danh sách nhiều người dùng có phân trang
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, obj_in: UserCreate) -> User:
    """
    Tạo mới một tài khoản người dùng và tự động mã hóa mật khẩu
    """
    hashed_password = get_password_hash(obj_in.password)
    db_user = User(
        username=obj_in.username,
        email=obj_in.email,
        hashed_password=hashed_password,
        role=obj_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, obj_in: UserUpdate) -> User:
    """
    Cập nhật thông tin tài khoản người dùng
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_user, field, update_data[field])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def change_password(db: Session, db_user: User, new_password: str) -> User:
    """
    Thay đổi mật khẩu tài khoản người dùng (tự động mã hóa mật khẩu mới)
    """
    db_user.hashed_password = get_password_hash(new_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Xác thực thông tin đăng nhập. Hỗ trợ đăng nhập bằng cả tên tài khoản (username) hoặc địa chỉ hòm thư (email).
    Trả về đối tượng User nếu hợp lệ, ngược lại trả về None.
    """
    user = get_user_by_username(db, username=username_or_email)
    if not user:
        user = get_user_by_email(db, email=username_or_email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
