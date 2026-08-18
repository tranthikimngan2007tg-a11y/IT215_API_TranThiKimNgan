# FlashMove RBAC + CORS

Project FastAPI thực hành về:
- Custom Middleware phân quyền theo vai trò.
- CORS Whitelist đa domain.
- Kiểm thử quyền truy cập và CORS.

## 1. Cài đặt

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

## 2. Chạy server

```bash
uvicorn main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 3. Vai trò

- DISPATCHER: gán đơn, cập nhật trạng thái, theo dõi đơn.
- DRIVER: cập nhật trạng thái, theo dõi đơn.
- CUSTOMER_SUPPORT: chỉ theo dõi đơn.

Header sử dụng:

```text
X-Role-Identity: DISPATCHER
```

## 4. API

### POST /api/v1/orders/assign
Chỉ `DISPATCHER`.

### PATCH /api/v1/orders/status
Cho `DISPATCHER` và `DRIVER`.

### GET /api/v1/orders/track
Cho cả:
- DISPATCHER
- DRIVER
- CUSTOMER_SUPPORT

## 5. Test Case

### Test 1 - DRIVER bị chặn

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/assign ^
  -H "X-Role-Identity: DRIVER"
```

Mong đợi:

```text
403 Forbidden
```

Body:

```json
{
  "status": "Rejected",
  "reason": "Unauthorized action for this role"
}
```

### Test 2 - DISPATCHER được phép

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/assign ^
  -H "X-Role-Identity: DISPATCHER"
```

Mong đợi:

```text
200 OK
```

### Test 3 - DRIVER cập nhật trạng thái

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/orders/status ^
  -H "X-Role-Identity: DRIVER"
```

Mong đợi:

```text
200 OK
```

### Test 4 - CUSTOMER_SUPPORT cập nhật trạng thái

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/orders/status ^
  -H "X-Role-Identity: CUSTOMER_SUPPORT"
```

Mong đợi:

```text
403 Forbidden
```

### Test 5 - CUSTOMER_SUPPORT theo dõi đơn

```bash
curl http://127.0.0.1:8000/api/v1/orders/track ^
  -H "X-Role-Identity: CUSTOMER_SUPPORT"
```

Mong đợi:

```text
200 OK
```

### Test 6 - CORS với origin hợp lệ

Preflight:

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/orders/track ^
  -H "Origin: https://driver.flashmove.io" ^
  -H "Access-Control-Request-Method: GET" ^
  -H "Access-Control-Request-Headers: X-Role-Identity"
```

Mong đợi có:

```text
Access-Control-Allow-Origin: https://driver.flashmove.io
```

### Test 7 - CORS với origin không hợp lệ

```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/orders/track ^
  -H "Origin: https://evil-competitor.com" ^
  -H "Access-Control-Request-Method: GET" ^
  -H "Access-Control-Request-Headers: X-Role-Identity"
```

Mong đợi:
- Không có `Access-Control-Allow-Origin: https://evil-competitor.com`.
- Domain lạ không được CORS whitelist.

## 6. CORS đang cho phép

Origins:

```text
https://driver.flashmove.io
https://hub.flashmove.io
```

Methods:

```text
GET
POST
PATCH
```

Headers:

```text
Content-Type
X-Role-Identity
```

Không sử dụng:

```python
allow_origins=["*"]
```
