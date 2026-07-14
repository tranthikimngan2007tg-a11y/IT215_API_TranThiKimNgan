

# 1. Chỉ ra lỗi

# | STT | Hành vi lỗi trong code hiện tại | Hậu quả đối với Database MySQL | Cách khắc phục bằng SQLAlchemy |
# |-----|---------------------------------|--------------------------------|--------------------------------|
# | 1 | Thiếu lệnh db.commit() | Dữ liệu không được lưu vào bảng products mặc dù API trả về thành công. | Thêm db.commit() sau db.add(new_product). |
# | 2 | Không đóng Session (db.close()) | Kết nối đến MySQL không được giải phóng, nhiều request có thể làm đầy Connection Pool. | Đóng Session bằng db.close(), nên đặt trong khối finally. |

# ------------------------------------------------------------

# 2. Code sau khi sửa

from fastapi import FastAPI, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float

app = FastAPI()

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    db = SessionLocal()

    try:
        new_product = ProductModel(
            sku=product.sku,
            name=product.name,
            price=product.price
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "message": "Product created successfully",
            "data": {
                "id": new_product.id,
                "sku": new_product.sku,
                "name": new_product.name,
                "price": new_product.price
            }
        }

    finally:
        db.close()