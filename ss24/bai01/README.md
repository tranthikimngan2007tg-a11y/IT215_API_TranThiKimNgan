# MegaMart ERP - RBAC & CORS

Project FastAPI thực hiện bài tập xây dựng **Middleware phân quyền tập trung (RBAC)** và **CORS nghiêm ngặt**.

## 1. Chức năng

### Vai trò
- `ADMIN`: truy cập mọi API.
- `HR`: quản lý thông tin nhân viên/bảng lương.
- `STAFF`: chỉ xem thông tin cá nhân.

### API
- `GET /api/v1/salary/modify` -> `ADMIN`, `HR`
- `GET /api/v1/system/settings` -> `ADMIN`
- `GET /api/v1/profile` -> `ADMIN`, `HR`, `STAFF`
- `GET /health` -> công khai

### Header giả lập role
Gửi:

```text
X-User-Role: ADMIN
```

hoặc:

```text
X-User-Role: HR
```

hoặc:

```text
X-User-Role: STAFF
```

Middleware sẽ trả `403` và JSON:

```json
{"error": "Permission Denied"}
```

nếu role không được phép.

## 2. CORS

Chỉ cho phép:

```text
https://internal.megamart.com
```

Methods:

```text
GET, POST
```

Headers:

```text
Content-Type, X-User-Role
```

Không dùng `allow_origins=["*"]`.

## 3. Cài đặt

Mở terminal tại thư mục project:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

Chạy server:

```bash
uvicorn main:app --reload
```

Mở Swagger:

```text
http://127.0.0.1:8000/docs
```

## 4. Test phân quyền

### STAFF -> system settings

Request:

```text
GET /api/v1/system/settings
X-User-Role: STAFF
```

Kết quả:

```text
403 Forbidden
```

```json
{"error":"Permission Denied"}
```

### ADMIN -> system settings

Request:

```text
GET /api/v1/system/settings
X-User-Role: ADMIN
```

Kết quả:

```text
200 OK
```

### HR -> salary

Request:

```text
GET /api/v1/salary/modify
X-User-Role: HR
```

Kết quả:

```text
200 OK
```

### STAFF -> salary

Request:

```text
GET /api/v1/salary/modify
X-User-Role: STAFF
```

Kết quả:

```text
403 Forbidden
```

### STAFF -> profile

Request:

```text
GET /api/v1/profile
X-User-Role: STAFF
```

Kết quả:

```text
200 OK
```

## 5. Test CORS

### Origin hợp lệ

Request:

```text
Origin: https://internal.megamart.com
```

Backend có thể trả:

```text
Access-Control-Allow-Origin: https://internal.megamart.com
```

### Origin không hợp lệ

Request:

```text
Origin: https://evil-attacker.xyz
```

Backend **không trả**:

```text
Access-Control-Allow-Origin: https://evil-attacker.xyz
```

Do đó trình duyệt sẽ chặn việc đọc response theo chính sách CORS.

## 6. Test CORS preflight

Ví dụ:

```bash
curl -i -X OPTIONS "http://127.0.0.1:8000/api/v1/profile" ^
  -H "Origin: https://internal.megamart.com" ^
  -H "Access-Control-Request-Method: GET" ^
  -H "Access-Control-Request-Headers: X-User-Role"
```

Preflight không bị RBAC chặn vì middleware bỏ qua `OPTIONS` để `CORSMiddleware` xử lý.

## 7. Header hệ thống

Các response đi qua middleware sẽ có:

```text
X-System-Name: MegaMart ERP
```

## 8. Lưu ý kiến trúc

Bài tập sử dụng `X-User-Role` để **giả lập danh tính/vai trò**. Trong hệ thống thực tế, role nên được lấy từ JWT/session đã xác thực thay vì tin trực tiếp một header do client tự gửi.
