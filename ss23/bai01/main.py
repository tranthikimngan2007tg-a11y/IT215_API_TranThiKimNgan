from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

app = FastAPI(title="JWT Authentication Training")

SECRET_KEY = "training-secret-key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

USERS = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Nguyen",
        "role": "user",
        "is_active": True,
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Tran",
        "role": "user",
        "is_active": False,
    },
}


@app.get("/issue-token/{username}")
def issue_token(username: str, expired: bool = False):
    if username not in USERS:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=-5 if expired else 30
    )

    token = jwt.encode(
        {
            "sub": username,
            "exp": expires_at,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # jwt.decode() kiểm tra chữ ký và thời hạn exp.
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Kiểm tra trường sub
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Kiểm tra tài khoản có tồn tại
    user = USERS.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Kiểm tra tài khoản có đang hoạt động
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


@app.get("/users/me")
def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user


# Lỗi của chương trình nằm ở việc sử dụng jwt.get_unverified_claims(token).
# Hàm này chỉ đọc payload của JWT mà không xác minh chữ ký bằng SECRET_KEY
# và không bảo đảm token còn thời hạn.

# Vì vậy:
# 1. Token hết hạn vẫn có thể truy cập /users/me.
# 2. Người dùng có thể sửa trường sub trong payload để giả mạo tài khoản khác.
# 3. Tài khoản bị khóa vẫn có thể truy cập vì code chưa kiểm tra is_active.

# Cách sửa:
# - Sử dụng jwt.decode() để kiểm tra chữ ký và thời hạn exp.
# - Kiểm tra trường sub có tồn tại hay không.
# - Kiểm tra username có tồn tại trong USERS hay không.
# - Kiểm tra is_active của tài khoản.

# Quy tắc trả về:
# - 401 Unauthorized: token không hợp lệ, hết hạn, thiếu sub,
#   sai chữ ký hoặc user không tồn tại.
# - 403 Forbidden: token hợp lệ nhưng tài khoản đã bị khóa.
