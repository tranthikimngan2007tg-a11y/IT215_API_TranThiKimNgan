# BÀI LÀM

# 1. Chỉ ra lỗi

# | STT | Phương thức truy vấn hiện tại | Tình huống gây lỗi (Edge Case) | Phương thức thay thế an toàn hơn |
# |-----|-------------------------------|--------------------------------|----------------------------------|
# | 1 | .one() | Khi order_id = 999 không tồn tại trong database, .one() sẽ phát sinh ngoại lệ và API trả về lỗi 500. | Dùng .first() kết hợp kiểm tra if order is None rồi trả về HTTPException(status_code=404). |

# ------------------------------------------------------------

# 2. Code sau khi sửa

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100))
    total_price = Column(Integer)

app = FastAPI()

@app.get("/orders/{order_id}")
def get_order_detail(order_id: int):
    db = SessionLocal()

    try:
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id
        ).first()

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        return {
            "id": order.id,
            "customer": order.customer_name
        }

    finally:
        db.close()
# ```

# ------------------------------------------------------------

# 3. Test case 1 - Đơn hàng tồn tại

# Request

# GET /orders/1

# Kết quả mong đợi

# Status Code:

# 200 OK

# Response

# ```json
# {
#     "id": 1,
#     "customer": "Nguyen Van A"
# }
# ```

# => PASS: API trả về đúng thông tin đơn hàng.

# ------------------------------------------------------------

# 4. Test case 2 - Đơn hàng không tồn tại (Edge Case)

# Request

# GET /orders/999

# Kết quả mong đợi

# Status Code:

# 404 Not Found

# Response

# ```json
# {
#     "detail": "Order not found"
# }
# ```

# => PASS: API không bị crash, không trả về Stack Trace, xử lý đúng lỗi 404 theo yêu cầu.