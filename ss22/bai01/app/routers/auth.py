from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from sqlalchemy.orm import Session

from app.cores.security import decode_access_token

from app.db.database import get_db

from app.schemas.user import (
    UserLogin,
    UserRegister,
    TokenResponse
)

from app.services.user import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/api",
    tags=["Authentication"]
)


security = HTTPBearer()


@router.post("/register")
def register(
    request: UserRegister,
    db: Session = Depends(get_db)
):

    user = register_user(
        db,
        request.username,
        request.password
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    return {
        "message": "Register successfully",
        "username": user.username
    }


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: UserLogin,
    db: Session = Depends(get_db)
):

    token = login_user(
        db,
        request.username,
        request.password
    )

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/profile")
def profile(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):

    token = credentials.credentials

    payload = decode_access_token(
        token
    )

    username = payload.get("sub")

    if not username:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {
        "message": f"Welcome, {username}!"
    }