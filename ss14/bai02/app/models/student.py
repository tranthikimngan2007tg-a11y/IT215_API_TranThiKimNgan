from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    major = Column(String(100), nullable=False)
    gpa = Column(Float, nullable=False)
