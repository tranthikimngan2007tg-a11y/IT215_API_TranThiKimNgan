from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# ==========================
# DỮ LIỆU ĐĂNG KÝ KHÓA HỌC
# ==========================

enrollments = [
    {
        "id": 1,
        "student_id": "SV001",
        "course_id": 1
    },
    {
        "id": 2,
        "student_id": "SV002",
        "course_id": 1
    }
]

# Schema đăng ký khóa học
class EnrollmentCreate(BaseModel):
    student_id: str
    course_id: int


# ==================================================
# PHẦN 1. PHÂN TÍCH LỖI BẰNG TEST CASE
# ==================================================

# Test case 1
#
# Dữ liệu gửi lên:
#
# {
#     "student_id": "SV001",
#     "course_id": 1
# }
#
# Kết quả hiện tại:
# API vẫn tạo thêm bản ghi đăng ký mới.
#
# Kết quả đúng mong muốn:
# Báo lỗi vì học viên đã đăng ký khóa học này.
#
# Lỗi phát hiện:
# API không kiểm tra đăng ký trùng trước khi thêm dữ liệu.


# Test case 2
#
# Dữ liệu gửi lên:
#
# {
#     "student_id": "SV002",
#     "course_id": 1
# }
#
# Kết quả hiện tại:
# API vẫn tạo thêm bản ghi đăng ký mới.
#
# Kết quả đúng mong muốn:
# Báo lỗi vì học viên đã đăng ký khóa học này.
#
# Lỗi phát hiện:
# API cho phép một học viên đăng ký cùng một khóa học nhiều lần.


# ==================================================
# PHẦN 2. SỬA SOURCE CODE
# ==================================================

@app.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment: EnrollmentCreate):

    # Kiểm tra học viên đã đăng ký khóa học này hay chưa
    for item in enrollments:
        if (
            item["student_id"] == enrollment.student_id
            and item["course_id"] == enrollment.course_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Học viên đã đăng ký khóa học này"
            )

    # Nếu chưa đăng ký thì tạo mới
    new_enrollment = {
        "id": len(enrollments) + 1,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id
    }

    enrollments.append(new_enrollment)

    return {
        "message": "Enroll successfully",
        "data": new_enrollment
    }


# ==================================================
# PHẦN 3. TEST SAU KHI SỬA
# ==================================================

# Test 1
#
# Request:
#
# POST /enrollments
#
# {
#     "student_id": "SV001",
#     "course_id": 1
# }
#
# Kết quả mong muốn:
#
# Status Code: 400
#
# {
#     "detail": "Học viên đã đăng ký khóa học này"
# }


# Test 2
#
# Request:
#
# POST /enrollments
#
# {
#     "student_id": "SV003",
#     "course_id": 1
# }
#
# Kết quả mong muốn:
#
# Status Code: 201
#
# {
#     "message": "Enroll successfully",
#     "data": {
#         "id": 3,
#         "student_id": "SV003",
#         "course_id": 1
#     }
# }


# ==================================================
# PHẦN 4. KẾT LUẬN
# ==================================================

# - API Create dùng để thêm mới dữ liệu đăng ký khóa học.
#
# - Trước khi tạo đăng ký mới cần kiểm tra học viên đã đăng ký
#   khóa học đó hay chưa.
#
# - Điều kiện kiểm tra là student_id và course_id phải cùng trùng nhau.
#
# - Nếu đã tồn tại thì trả về HTTPException.
#
# - Nếu chưa tồn tại thì cho phép tạo đăng ký mới.
#
# - Khi đăng ký thành công, API trả về HTTP Status Code 201 Created.
#
# - Việc kiểm tra đăng ký trùng giúp đảm bảo dữ liệu chính xác,
#   tránh một học viên đăng ký cùng một khóa học nhiều lần.