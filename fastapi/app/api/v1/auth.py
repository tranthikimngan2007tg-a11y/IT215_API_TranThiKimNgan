from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.crud import crud_user, crud_student, crud_class
from app.schemas.auth import Token, LoginRequest
from app.schemas.user import UserResponse, UserCreate, UserChangePassword
from app.schemas.student import StudentRegister, StudentResponse
from app.schemas.response import APIResponse
from app.api import deps
from app.models.user import UserRole

router = APIRouter()


@router.post("/login", response_model=APIResponse[Token], summary="Đăng nhập chuẩn OAuth2 (nhận form-data)")
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> APIResponse[Token]:
    """
    Đăng nhập tương thích với chuẩn OAuth2 để lấy JWT access_token cho các yêu cầu tiếp theo.
    Hỗ trợ nhập tên tài khoản (username) hoặc địa chỉ hòm thư (email) vào trường 'username'.
    """
    user = crud_user.authenticate(
        db, username_or_email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập/email hoặc mật khẩu không chính xác."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.username, role=user.role, expires_delta=access_token_expires
    )
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role
    )
    return APIResponse[Token](
        statusCode=status.HTTP_200_OK,
        message="Đăng nhập thành công.",
        data=token_data
    )

@router.post("/login/json", response_model=APIResponse[Token], summary="Đăng nhập qua định dạng JSON")
def login_json(
    db: Session = Depends(get_db), credentials: LoginRequest = None
) -> APIResponse[Token]:
    """
    Đường dẫn đăng nhập thay thế chấp nhận request body dạng JSON thay vì form-data.
    """
    if not credentials:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp đầy đủ thông tin đăng nhập.")
    user = crud_user.authenticate(
        db, username_or_email=credentials.username, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập/email hoặc mật khẩu không chính xác."
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.username, role=user.role, expires_delta=access_token_expires
    )
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role
    )
    return APIResponse[Token](
        statusCode=status.HTTP_200_OK,
        message="Đăng nhập thành công.",
        data=token_data
    )

@router.post("/register/lecturer", response_model=APIResponse[UserResponse], summary="Đăng ký tài khoản Giảng viên")
def register_lecturer(
    user_in: UserCreate, db: Session = Depends(get_db)
) -> APIResponse[UserResponse]:
    """
    Đăng ký một tài khoản giảng viên mới (quyền mặc định: lecturer).
    """
    user_in.role = UserRole.LECTURER  # Bắt buộc phân quyền Giảng viên
    user_exists = crud_user.get_user_by_username(db, username=user_in.username)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại trong hệ thống."
        )
    email_exists = crud_user.get_user_by_email(db, email=user_in.email)
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email đã được đăng ký."
        )
    new_user = crud_user.create_user(db, obj_in=user_in)
    return APIResponse[UserResponse](
        statusCode=status.HTTP_201_CREATED,
        message="Đăng ký tài khoản giảng viên thành công.",
        data=new_user
    )

@router.post("/register/student", response_model=APIResponse[StudentResponse], summary="Đăng ký tài khoản và hồ sơ Sinh viên")
def register_student(
    student_in: StudentRegister, db: Session = Depends(get_db)
) -> APIResponse[StudentResponse]:
    """
    Tạo tài khoản sinh viên mới đồng thời chèn dữ liệu vào bảng hồ sơ sinh viên chi tiết.
    """
    user_exists = crud_user.get_user_by_username(db, username=student_in.username)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại trong hệ thống."
        )
    email_exists = crud_user.get_user_by_email(db, email=student_in.email)
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Địa chỉ email đã được sử dụng."
        )
    code_exists = crud_student.get_student_by_code(db, student_code=student_in.student_code)
    if code_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã sinh viên đã được cấp cho người khác."
        )
    
    if student_in.class_id is not None:
        db_class = crud_class.get_class_by_id(db, class_id=student_in.class_id)
        if not db_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy lớp học."
            )
            
    db_student = crud_student.register_student(db, obj_in=student_in)
    return APIResponse[StudentResponse](
        statusCode=status.HTTP_201_CREATED,
        message="Đăng ký tài khoản và thông tin sinh viên thành công.",
        data=db_student
    )

@router.get("/me", response_model=APIResponse[UserResponse], summary="Lấy thông tin tài khoản hiện tại")
def read_user_me(
    current_user: UserResponse = Depends(deps.get_current_active_user)
) -> APIResponse[UserResponse]:
    """
    Lấy thông tin chi tiết tài khoản của người dùng đang đăng nhập dựa trên token.
    """
    return APIResponse[UserResponse](
        statusCode=status.HTTP_200_OK,
        message="Lấy thông tin người dùng hiện tại thành công.",
        data=current_user
    )

@router.put("/me/password", response_model=APIResponse[UserResponse], summary="Thay đổi mật khẩu cá nhân")
def update_password_me(
    password_in: UserChangePassword,
    current_user: UserResponse = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db)
) -> APIResponse[UserResponse]:
    """
    Cho phép người dùng tự cập nhật lại mật khẩu tài khoản của mình.
    """
    if not security.verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không chính xác."
        )
    updated_user = crud_user.change_password(db, db_user=current_user, new_password=password_in.new_password)
    return APIResponse[UserResponse](
        statusCode=status.HTTP_200_OK,
        message="Thay đổi mật khẩu tài khoản thành công.",
        data=updated_user
    )
