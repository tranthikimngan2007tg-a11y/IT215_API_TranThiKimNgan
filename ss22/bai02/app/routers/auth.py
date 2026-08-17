from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse
)

from app.services.user import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/api/v1/medical",
    tags=["Medical"]
)


@router.post("/register")
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):

    user = register_user(
        db,
        data.username,
        data.password,
        data.role
    )

    if not user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return {
        "message": "Register successfully",
        "username": user.username,
        "role": user.role
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):

    token = login_user(
        db,
        data.username,
        data.password
    )

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không chính xác"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }