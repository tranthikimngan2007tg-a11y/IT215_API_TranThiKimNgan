from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/shop_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)


class CustomerUpdate(BaseModel):
    full_name: str
    phone: str
    address: str


app = FastAPI()


# Dependency quản lý Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    # Tìm khách hàng
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id
    ).first()

    # Nếu không tồn tại
    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Cập nhật thông tin
    customer.full_name = customer_update.full_name
    customer.phone = customer_update.phone
    customer.address = customer_update.address

    # Lưu vào MySQL
    db.commit()

    # Lấy dữ liệu mới nhất
    db.refresh(customer)

    # Trả kết quả
    return {
        "message": "Customer updated successfully",
        "data": {
            "id": customer.id,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "address": customer.address
        }
    }