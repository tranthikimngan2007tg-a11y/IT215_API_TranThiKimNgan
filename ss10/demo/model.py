# Dùng để cấu hình bảng và cột của dữ liệu
from database import Base
from sqlalchemy import Column, Integer, String

class StudenModel(Base):
    __tablename__= "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)