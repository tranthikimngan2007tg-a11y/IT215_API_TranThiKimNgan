# Learning Management System - FastAPI Security Practice

## 1. Mục tiêu

Sửa lỗi authentication, authorization, CORS và middleware theo yêu cầu đề bài.

Quy tắc sau khi sửa:

- `admin-token` được xóa khóa học.
- `user-token` không được xóa khóa học.
- `locked-token` không được truy cập API bảo vệ.
- `/health` không yêu cầu JWT.
- `OPTIONS` không bị middleware authentication chặn.
- Chỉ cho phép CORS từ:
  - `http://localhost:3000`
  - `http://localhost:5173`
- Không dùng `allow_origins=["*"]`.
- Response có `X-System-Name: Learning Management System`.

## 2. Cài đặt

Tạo môi trường ảo (khuyến nghị):

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

## 3. Chạy chương trình

```bash
uvicorn main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 4. Các token mẫu

| Token | Username | Role | Active |
|---|---|---|---|
| `admin-token` | `admin01` | admin | true |
| `user-token` | `student01` | user | true |
| `locked-token` | `locked01` | user | false |

Với OAuth2 Bearer, gửi header:

```text
Authorization: Bearer admin-token
```

## 5. Test case

### Test 1 - User xóa khóa học

```http
DELETE /admin/courses/1
Authorization: Bearer user-token
```

Kỳ vọng:

```text
403 Forbidden
```

### Test 2 - Admin xóa khóa học

```http
DELETE /admin/courses/1
Authorization: Bearer admin-token
```

Kỳ vọng:

```text
200 OK
```

Ví dụ:

```json
{
  "message": "Course 1 has been deleted",
  "deleted_by": "admin01"
}
```

### Test 3 - Locked user truy cập API bảo vệ

```http
GET /courses
Authorization: Bearer locked-token
```

Kỳ vọng:

```text
403 Forbidden
```

### Test 4 - /health không cần đăng nhập

```http
GET /health
```

Kỳ vọng:

```text
200 OK
```

Body:

```json
{
  "status": "UP"
}
```

### Test 5 - CORS preflight hợp lệ

```http
OPTIONS /courses
Origin: http://localhost:5173
Access-Control-Request-Method: GET
Access-Control-Request-Headers: Authorization
```

Kỳ vọng:

- Không trả `401` do thiếu Authorization.
- Có `Access-Control-Allow-Origin: http://localhost:5173`.
- Có các CORS header phù hợp cho preflight.

### Test 6 - Website không được phép

```http
OPTIONS /courses
Origin: https://unknown-website.com
Access-Control-Request-Method: GET
```

Kỳ vọng:

- Không có `Access-Control-Allow-Origin: https://unknown-website.com`.
- Website không được cấp quyền CORS.

## 6. Các lỗi đã sửa

### Lỗi 1 - Sai điều kiện trong `require_admin()`

Code cũ:

```python
if current_user["role"] == "admin" or current_user["is_active"]:
```

Sai vì chỉ cần `is_active=True` thì user thường cũng được đi tiếp.

Code đúng:

```python
if current_user["role"] != "admin":
    raise HTTPException(status_code=403, detail="Admin permission required")
```

### Lỗi 2 - Middleware yêu cầu Authorization với mọi request

Code cũ chặn cả `/health` và request không có JWT.

Code mới bỏ qua authentication middleware cho `/health`.

### Lỗi 3 - Middleware chặn OPTIONS

CORS preflight dùng `OPTIONS`. Nếu middleware yêu cầu Authorization trước khi request tới CORS middleware thì preflight có thể bị `401`.

Code mới cho `OPTIONS` đi qua middleware authentication.

### Lỗi 4 - CORS cho phép mọi nguồn

Code cũ:

```python
allow_origins=["*"]
```

Code mới chỉ cho:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

## 7. Lưu ý về thứ tự middleware

FastAPI/Starlette áp dụng middleware theo thứ tự lớp. `CORSMiddleware` được thêm vào app và middleware authentication kiểm tra `OPTIONS` để không ngăn cản CORS preflight. Cách tổ chức này đáp ứng yêu cầu bài tập và vẫn giữ header `X-System-Name` cho các response đi qua authentication middleware.
