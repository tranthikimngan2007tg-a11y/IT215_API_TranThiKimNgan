from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    status = Column(String(20), nullable=False)

    # Một sinh viên có thể đăng ký nhiều workshop.
    registrations = relationship("Registration", back_populates="student")


class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))
    maximum_participants = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)

    # Một workshop có nhiều sinh viên đăng ký.
    registrations = relationship("Registration", back_populates="workshop")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)

    # Khóa ngoại liên kết đến bảng Student.
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    # Khóa ngoại liên kết đến bảng Workshop.
    workshop_id = Column(Integer, ForeignKey("workshops.id"), nullable=False)

    registered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="REGISTERED")

    # Mỗi Registration chỉ thuộc về một Student.
    student = relationship("Student", back_populates="registrations")

    # Mỗi Registration chỉ thuộc về một Workshop.
    workshop = relationship("Workshop", back_populates="registrations")