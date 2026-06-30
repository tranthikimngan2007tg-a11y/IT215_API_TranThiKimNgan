# (1) PHÂN TÍCH INPUT / OUTPUT
#
# - Input:
#   + Danh sách books gồm các thông tin:
#       id, title, quantity.
#
# - Output:
#   + Trả về một đối tượng JSON gồm:
#       message: Thông báo kết quả.
#       data: Danh sách sách sắp hết hàng.
#
# - Điều kiện xác định sách sắp hết hàng:
#   + quantity <= 5

# (2) ĐỀ XUẤT GIẢI PHÁP
#
# Giải pháp 1:
# - Sử dụng vòng lặp for kết hợp if.
# - Dễ kiểm tra dữ liệu thiếu hoặc không hợp lệ.
#
# Giải pháp 2:
# - Sử dụng List Comprehension.
# - Code ngắn gọn nhưng khó xử lý nhiều điều kiện.

# (3) SO SÁNH VÀ LỰA CHỌN
#
# Tiêu chí                  Vòng lặp for      List Comprehension
# --------------------------------------------------------------
# Độ dễ hiểu                Dễ                Trung bình
# Độ ngắn gọn              Trung bình        Tốt
# Dễ xử lý bẫy dữ liệu      Tốt               Khó hơn
# Dễ bảo trì               Tốt               Trung bình

# Lựa chọn:
# - Chọn giải pháp dùng vòng lặp for vì dễ đọc,
#   dễ xử lý dữ liệu thiếu, dữ liệu sai và phù hợp
#   với bài toán thực tế.

# (4) THIẾT KẾ CÁC BƯỚC XỬ LÝ

# 1. Khởi tạo ứng dụng FastAPI.
# 2. Khai báo danh sách books.
# 3. Tạo endpoint GET /books/low-stock.
# 4. Duyệt từng quyển sách.
# 5. Nếu thiếu quantity thì bỏ qua.
# 6. Nếu quantity < 0 thì bỏ qua.
# 7. Nếu quantity <= 5 thì thêm vào danh sách kết quả.
# 8. Nếu danh sách kết quả rỗng:
#       Trả về message "Không có sách nào sắp hết hàng".
# 9. Ngược lại trả về danh sách sách sắp hết hàng.

# (5) TRIỂN KHAI

from fastapi import FastAPI
app = FastAPI()

books = [
    {"id": 1, "title": "Python Basic", "quantity": 12},
    {"id": 2, "title": "FastAPI Beginner", "quantity": 3},
    {"id": 3, "title": "Clean Code", "quantity": 5},
    {"id": 4, "title": "Database Design", "quantity": 0},
    {"id": 5, "title": "Web API Design", "quantity": 20},
    {"id": 6, "title": "Java Basic"},                  # Thiếu quantity
    {"id": 7, "title": "Spring Boot", "quantity": -2}  # Quantity không hợp lệ
]


@app.get("/books/low-stock")
def get_low_stock_books():
    low_stock_books = []

    for book in books:
        # Bỏ qua nếu thiếu quantity
        if "quantity" not in book:
            continue

        # Bỏ qua nếu quantity âm
        if book["quantity"] < 0:
            continue

        # Lấy sách có số lượng <= 5
        if book["quantity"] <= 5:
            low_stock_books.append(book)

    if len(low_stock_books) == 0:
        return {
            "message": "Không có sách nào sắp hết hàng",
            "data": []
        }

    return {
        "message": "Danh sách sách sắp hết hàng",
        "data": low_stock_books
    }