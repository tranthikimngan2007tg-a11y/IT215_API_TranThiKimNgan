# Hệ thống Quản lý Sinh viên (Student Management System API)

Hệ thống API quản lý sinh viên được xây dựng dựa trên nền tảng **FastAPI**, sử dụng **MySQL** làm Database chính và **SQLAlchemy (ORM)** để quản lý dữ liệu. Hệ thống áp dụng kiến trúc chuẩn doanh nghiệp (Clean/Layered Architecture) giúp dễ dàng mở rộng và bảo trì.

Dự án đã được cấu hình tối ưu để tương thích hoàn toàn với các phiên bản Python mới nhất (bao gồm cả phiên bản thử nghiệm **Python 3.14** trên Windows) bằng các cơ chế tự động nhận diện và cấu hình phiên bản linh hoạt.

---

## 🚀 Tính Năng Chính

1. **Quản lý Thông tin (CRUD)**:
   - Quản lý Sinh viên (Students), Lớp học (Classes), và Điểm số (Scores).
   - Kiểm tra dữ liệu đầu vào (data validation) nghiêm ngặt bằng **Pydantic v2** với các validators kiểm tra định dạng và logic tuổi sinh viên.
2. **Hệ thống Tìm kiếm Nâng cao**:
   - Tìm kiếm sinh viên theo tên (First/Last name), mã sinh viên, giới tính, lớp học, ngày sinh.
   - Tối ưu hóa hiệu năng truy vấn bằng **SQL Index** (Single & Composite Indexes).
3. **Bảo mật & Phân quyền (RBAC)**:
   - Đăng ký, đăng nhập và cấp phát token truy cập **JWT (JSON Web Token)**.
   - Phân quyền hai vai trò: **Giảng viên (Lecturer)** và **Sinh viên (Student)**.
     - _Giảng viên_: Có toàn quyền CRUD Lớp học, Sinh viên và Điểm số.
     - _Sinh viên_: Chỉ có quyền xem thông tin cá nhân của mình, xem điểm số và tính điểm trung bình tích lũy (GPA) của bản thân.
4. **Tài liệu Tự động**:
   - Hệ thống **Swagger UI** và **ReDoc** tự động cập nhật trực quan theo logic code (hoàn toàn bằng tiếng Việt).
5. **Cấu hình CI/CD**:
   - File cấu hình GitHub Actions tự động kiểm tra cú pháp, chạy tests và build Docker phục vụ auto deploy trên môi trường container.

---

## 📂 Cấu Trúc Thư Mục Chuẩn Doanh Nghiệp

```text
FastAPI/
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # Luồng chạy CI/CD (GitHub Actions)
├── app/
│   ├── api/
│   │   ├── deps.py           # Dependency injection (JWT, kiểm tra vai trò RBAC)
│   │   └── v1/
│   │       ├── api.py        # Master Router tổng hợp các router con
│   │       ├── auth.py       # API Đăng ký, Đăng nhập, Profile cá nhân
│   │       ├── classes.py    # API CRUD Lớp học
│   │       ├── scores.py     # API CRUD Điểm số & tính GPA
│   │       └── students.py   # API CRUD & Tìm kiếm Sinh viên nâng cao
│   ├── core/
│   │   ├── config.py         # Đọc cấu hình từ .env và quản lý settings
│   │   ├── database.py       # Cấu hình SQLAlchemy Engine, Session
│   │   └── security.py       # Mã hóa mật khẩu & xử lý JWT Token
│   ├── models/               # Khai báo các SQLAlchemy database models
│   │   ├── class_room.py
│   │   ├── score.py
│   │   ├── student.py
│   │   └── user.py
│   ├── schemas/              # Các Pydantic Schemas validate dữ liệu đầu vào/ra
│   │   ├── auth.py
│   │   ├── class_room.py
│   │   ├── score.py
│   │   ├── student.py
│   │   └── user.py
│   ├── initial_data.py       # Script seed dữ liệu mẫu ban đầu để test nhanh
│   └── main.py               # File chạy chính (Main entrypoint)
├── tests/                    # Thư mục chứa các unit/integration test cases
│   ├── conftest.py           # Thiết lập Database SQLite tạm thời chạy test
│   └── test_api.py           # Các kịch bản test API tự động
├── .env                      # File cấu hình môi trường chạy thực tế
├── .env.example              # File mẫu cấu hình môi trường
├── .gitignore                # Chặn các file rác python, venv, env
├── requirements.txt          # Các thư viện phụ thuộc của dự án
└── README.md                 # Hướng dẫn sử dụng hệ thống
```

---

## 🛠️ Hướng Dẫn Cài Đặt & Chạy Môi Trường Local

### Yêu cầu hệ thống

- **Python**: Phiên bản 3.10 trở lên (Tương thích tốt với 3.12, 3.13 và **3.14**).
- **MySQL Database** (Nếu chạy thực tế) hoặc **SQLite** (Mặc định chạy thử nhanh).

### Bước 1: Tạo và kích hoạt môi trường ảo (Virtual Environment)

Mở terminal tại thư mục dự án `d:\Rikkei Education\FastAPI`.

```bash
# Tạo môi trường ảo python
python -m venv venv

# Kích hoạt trên Windows (Powershell)
.\venv\Scripts\Activate.ps1

# Hoặc kích hoạt trên Windows (CMD)
.\venv\Scripts\activate.bat
```

### Bước 2: Cài đặt các thư viện cần thiết

Dự án sử dụng các phiên bản linh hoạt để đảm bảo cài đặt thành công trên các phiên bản Python mới nhất, đồng thời khóa phiên bản `bcrypt<5.0.0` để tương thích hoàn toàn với thư viện `passlib`.

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình Môi trường (.env)

Dự án được cấu hình mặc định để sử dụng **SQLite** (`DATABASE_URL=sqlite:///./student_management.db`) nhằm giúp bạn chạy thử nhanh nhất.
Nếu bạn muốn chuyển sang sử dụng **MySQL**, hãy sửa file `.env` như sau:

```env
PROJECT_NAME="Student Management System API"
API_V1_STR="/api/v1"

# Security
SECRET_KEY="e4a9e4b7c6ad22fe07328bfb0e35dc8f5539ab1377be836109dc090e9e4210a5"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120

# Database Configuration (MySQL)
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=my_password_mysql
MYSQL_DB=student_management

# Use SQLite by default for easy test/run out of the box, can be switched to MySQL
# DATABASE_URL=sqlite:///./student_management.db
DATABASE_URL=mysql+pymysql://root:my_password_mysql@localhost:3306/student_management
```

_(Lưu ý: Hãy tạo trước một database trống tên là `student_management` trong MySQL của các thầy trước khi khởi động server)._

### Bước 4: Tạo Dữ Liệu Mẫu (Database Seeding)

Trên hệ điều hành Windows, hãy bật cờ mã hóa UTF-8 của Python để tránh lỗi hiển thị tiếng Việt trên Terminal:

```powershell
# Chạy trên Powershell
$env:PYTHONUTF8="1"
python -m app.initial_data

# Hoặc chạy trên CMD
set PYTHONUTF8=1
python -m app.initial_data
```

**Tài khoản mẫu được tạo tự động:**

1. **Giảng viên (Lecturer)**:
   - Username: `teacher_smith`
   - Password: `password123`
2. **Sinh viên (Student) 1**:
   - Username: `alice_green` (Mã sinh viên: `SV1001`, lớp: `JV2403`)
   - Password: `password123`
3. **Sinh viên (Student) 2**:
   - Username: `bob_jones` (Mã sinh viên: `SV1002`, lớp: `PY2404`)
   - Password: `password123`

### Bước 5: Khởi chạy Server Uvicorn Development

```powershell
# Thiết lập mã hóa UTF-8 (nếu chưa thiết lập)
$env:PYTHONUTF8="1"

# Chạy server
uvicorn app.main:app --reload
```

Hệ thống sẽ hoạt động tại địa chỉ: `http://localhost:8000`

---

## 📖 Tài Liệu API & Swagger UI

Sau khi server khởi chạy thành công, bạn có thể truy cập các liên kết tài liệu trực quan:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) (Dùng để test trực tiếp các API với mô tả tiếng Việt)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ⚡ Hướng Dẫn Sử Dụng API Quy Trình Nghiệp Vụ

### 1. Luồng Xác thực (Authentication)

- Sử dụng API `POST /api/v1/auth/login` (nhập form username & password).
- Hệ thống trả về `access_token` JWT và `role`.
- Copy giá trị token, click nút **Authorize** ở phía góc phải trên cùng của Swagger UI, nhập theo định dạng: `Bearer <token_của_bạn>` để có quyền truy cập các API bị hạn chế.

### 2. Phân Quyền Vai Trò (Role-Based Access Control)

- **API Tạo Lớp Học / Điểm Số**: `POST /api/v1/classes/`, `POST /api/v1/scores/` chỉ giảng viên (`teacher_smith`) mới thực hiện thành công. Nếu dùng tài khoản của Alice (`alice_green`) gọi các API này, bạn sẽ nhận về lỗi `403 Forbidden`.
- **Xem thông tin sinh viên**: Sinh viên chỉ có thể gọi `GET /api/v1/students/{student_id}` đúng với `student_id` của mình.

### 3. Tìm kiếm Nâng cao & Phân trang (Advanced Search & Pagination)

API `GET /api/v1/students/search` hỗ trợ các tham số tìm kiếm tối ưu:

- `search_query` (Tìm theo họ tên, tên đệm hoặc mã sinh viên. VD: `Alice` hoặc `SV1001`).
- `class_id` (Lọc theo lớp).
- `gender` (Lọc theo giới tính: `Male`, `Female` hoặc `Other`).
- `dob_from` & `dob_to` (Lọc theo khoảng ngày sinh dạng `YYYY-MM-DD`).
- `skip` & `limit` (Phân trang dữ liệu).

> 💡 **Tối ưu hóa bằng SQL Index**:
> Trong database model `Student`, cột `student_code`, `first_name` và `last_name` đã được gắn index trực tiếp. Thêm vào đó, một Composite Index tên là `idx_student_name` được tạo cho cặp `(first_name, last_name)`. Cột `class_id` đóng vai trò khóa ngoại cũng được đánh index nhằm tăng tốc tối đa các câu lệnh JOIN và tìm kiếm theo lớp học.

### 4. Tính toán Điểm GPA

API `GET /api/v1/scores/student/{student_id}/gpa` tự động tổng hợp tất cả điểm số của sinh viên đó và tính điểm trung bình tích lũy theo trọng số của từng cột điểm:
$$\text{GPA} = \frac{\sum (\text{score\_value} \times \text{weight})}{\sum \text{weight}}$$

---

## 🧪 Chạy Kiểm Thử Tự Động (Automation Tests)

Để đảm bảo hệ thống hoạt động ổn định và kiểm tra việc phân quyền bảo mật có đúng logic, chạy lệnh test sau:

```bash
$env:PYTHONUTF8="1"
pytest -v
```

Dự án sử dụng SQLite in-memory tự động cho môi trường test nên bạn không lo bị lẫn lộn dữ liệu test vào database chính.
