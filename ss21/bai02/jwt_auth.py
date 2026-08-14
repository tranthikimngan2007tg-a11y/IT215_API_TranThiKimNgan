from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError, ExpiredSignatureError


# Secret key dùng để ký và kiểm tra JWT
SECRET_KEY = "my-super-secret-key-change-this-in-production"

# Thuật toán
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_minutes: int) -> str:
    """
    Tạo JWT Access Token.
    """

    # Copy data để không làm thay đổi dictionary ban đầu
    payload = data.copy()

    # Tính thời gian hết hạn
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    # Thêm thời gian hết hạn vào payload
    payload["exp"] = expire

    # Tạo và ký JWT
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decode_access_token(token: str) -> dict:
    """
    Giải mã và kiểm tra JWT.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except ExpiredSignatureError:
        raise ValueError("Token đã hết hạn")

    except JWTError:
        raise ValueError("Token không hợp lệ")


# =========================
# TEST
# =========================

token = create_access_token(
    data={
        "sub": "student01@gmail.com",
        "user_id": 1,
        "role": "student"
    },
    expires_minutes=30
)

print("TOKEN:")
print(token)

print("\nDECODE:")
print(decode_access_token(token))



# 1. Ba phần của JWT là gì?
# JWT gồm 3 phần, được ngăn cách bởi dấu chấm (.):
# Header.Payload.Signature
#
# - Header: Chứa thông tin về thuật toán ký (ví dụ HS256)
#   và loại token (JWT).
#
# - Payload: Chứa các thông tin của người dùng như:
#   sub, user_id, role, exp.
#
# - Signature: Được tạo từ Header, Payload và SECRET_KEY.
#   Dùng để kiểm tra token có bị giả mạo hoặc thay đổi hay không.


# 2. Payload của JWT có được mã hóa để che giấu dữ liệu hay không?
# Không.
# Payload của JWT không được mã hóa mà chỉ được mã hóa dạng
# Base64URL (encoding), vì vậy người khác vẫn có thể đọc được.
#
# Do đó không được đưa các thông tin bí mật như:
# password, password_hash, SECRET_KEY vào Payload.
#
# JWT chủ yếu đảm bảo tính toàn vẹn và xác thực của dữ liệu,
# không phải dùng để che giấu dữ liệu.


# 3. Signature có vai trò gì?
# Signature giúp server kiểm tra:
# - Token có được tạo bởi hệ thống hay không.
# - Payload và Header có bị thay đổi sau khi token được tạo hay không.
#
# Signature được tạo dựa trên:
# Header + Payload + SECRET_KEY
#
# Nếu người dùng sửa Payload, Signature cũ sẽ không còn hợp lệ
# và server sẽ từ chối token.


# 4. Điều gì xảy ra nếu người dùng tự sửa trường role trong Payload?
# Ví dụ token ban đầu có:
# "role": "student"
#
# Người dùng tự sửa thành:
# "role": "admin"
#
# Sau khi Payload bị sửa, Signature ban đầu không còn khớp.
# Khi server gọi decode_access_token(), JWT sẽ bị phát hiện
# là không hợp lệ và bị từ chối.
#
# Vì vậy người dùng không thể tự sửa role từ "student" thành
# "admin" mà vẫn sử dụng được token.