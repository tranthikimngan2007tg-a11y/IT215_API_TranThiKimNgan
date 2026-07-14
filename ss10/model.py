from database import Base
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel


class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)


class StudentRequestDTO(BaseModel):
    id: int
    full_name: str
    email: str