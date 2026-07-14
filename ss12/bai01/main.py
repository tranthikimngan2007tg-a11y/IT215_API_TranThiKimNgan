from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

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


class ProductUpdate(BaseModel):
    name: str
    price: float


app = FastAPI()


# Dependency quản lý Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    # Tìm sản phẩm
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()

    # Nếu không tồn tại
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Cập nhật dữ liệu
    product.name = product_update.name
    product.price = product_update.price

    # Lưu vào MySQL
    db.commit()

    # Lấy dữ liệu mới nhất
    db.refresh(product)

    # Trả kết quả
    return {
        "message": "Product updated successfully",
        "data": {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "price": product.price
        }
    }