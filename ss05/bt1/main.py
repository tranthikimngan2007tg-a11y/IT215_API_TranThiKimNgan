from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# ==========================
# DỮ LIỆU SẢN PHẨM
# ==========================

products = [
    {
        "id": 1,
        "code": "SP001",
        "name": "Laptop Dell",
        "price": 15000000,
        "stock": 10
    },
    {
        "id": 2,
        "code": "SP002",
        "name": "Mouse Logitech",
        "price": 350000,
        "stock": 50
    }
]

# Schema tạo sản phẩm
class ProductCreate(BaseModel):
    code: str
    name: str
    price: float
    stock: int


# ==================================================
# PHẦN 1. PHÂN TÍCH LỖI BẰNG TEST CASE
# ==================================================

# Test case 1
#
# Dữ liệu gửi lên:
#
# {
#     "code": "SP001",
#     "name": "Laptop Asus",
#     "price": 18000000,
#     "stock": 5
# }
#
# Kết quả hiện tại:
# API vẫn tạo thành công sản phẩm mới.
#
# Kết quả đúng mong muốn:
# Báo lỗi vì mã sản phẩm SP001 đã tồn tại.
#
# Lỗi phát hiện:
# API không kiểm tra trùng mã sản phẩm trước khi thêm dữ liệu.


# Test case 2
#
# Dữ liệu gửi lên:
#
# {
#     "code": "SP002",
#     "name": "Bàn phím cơ",
#     "price": 1200000,
#     "stock": 20
# }
#
# Kết quả hiện tại:
# API vẫn tạo thành công sản phẩm mới.
#
# Kết quả đúng mong muốn:
# Báo lỗi vì mã sản phẩm SP002 đã tồn tại.
#
# Lỗi phát hiện:
# API cho phép tạo nhiều sản phẩm có cùng mã sản phẩm.


# ==================================================
# PHẦN 2. SỬA SOURCE CODE
# ==================================================

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):

    # Kiểm tra mã sản phẩm đã tồn tại hay chưa
    for item in products:
        if item["code"] == product.code:
            raise HTTPException(
                status_code=400,
                detail="Mã sản phẩm đã tồn tại"
            )

    # Nếu mã sản phẩm chưa tồn tại thì tạo mới
    new_product = {
        "id": len(products) + 1,
        "code": product.code,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }

    products.append(new_product)

    return {
        "message": "Create product successfully",
        "data": new_product
    }


# ==================================================
# PHẦN 3. TEST SAU KHI SỬA
# ==================================================

# Test 1
#
# Request:
#
# POST /products
#
# {
#     "code": "SP001",
#     "name": "Laptop Asus",
#     "price": 18000000,
#     "stock": 5
# }
#
# Kết quả mong muốn:
#
# Status Code: 400
#
# {
#     "detail": "Mã sản phẩm đã tồn tại"
# }


# Test 2
#
# Request:
#
# POST /products
#
# {
#     "code": "SP003",
#     "name": "Tai nghe Sony",
#     "price": 990000,
#     "stock": 30
# }
#
# Kết quả mong muốn:
#
# Status Code: 201
#
# {
#     "message": "Create product successfully",
#     "data": {
#         "id": 3,
#         "code": "SP003",
#         "name": "Tai nghe Sony",
#         "price": 990000,
#         "stock": 30
#     }
# }


# ==================================================
# PHẦN 4. KẾT LUẬN
# ==================================================

# - API Create dùng để thêm mới dữ liệu.
#
# - Trước khi tạo sản phẩm cần kiểm tra mã sản phẩm có bị trùng hay không.
#
# - Nếu mã sản phẩm đã tồn tại thì không được tạo mới.
#
# - Khi phát hiện trùng mã sản phẩm, API trả về HTTPException.
#
# - Nếu mã sản phẩm chưa tồn tại thì thêm vào danh sách products.
#
# - Khi tạo thành công, API trả về HTTP Status Code 201 Created.
#
# - Việc kiểm tra trùng mã sản phẩm giúp đảm bảo tính chính xác và
#   nhất quán của dữ liệu trong hệ thống.