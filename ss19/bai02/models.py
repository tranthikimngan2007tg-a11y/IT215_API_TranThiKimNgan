from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


# ==========================
# Bảng Clinic
# Một Clinic có nhiều Doctor (1 - N)
# ==========================
class Clinic(Base):
    __tablename__ = "clinics"

    # Khóa chính
    id = Column(Integer, primary_key=True, index=True)

    # Tên phòng khám
    clinic_name = Column(String(100), nullable=False)

    # Chuyên khoa
    specialty = Column(String(100), nullable=False)

    # Quan hệ 1 - N
    # Một Clinic có nhiều Doctor
    doctors = relationship(
        "Doctor",
        back_populates="clinic"
    )


# ==========================
# Bảng Doctor
# Thuộc một Clinic
# Có một License (1 - 1)
# ==========================
class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)

    # Mã bác sĩ (không trùng)
    doctor_code = Column(String(50), unique=True, nullable=False)

    # Lương
    salary = Column(Float, nullable=False)

    # Khóa ngoại
    clinic_id = Column(Integer, ForeignKey("clinics.id"))

    # Quan hệ N - 1
    # Doctor thuộc về một Clinic
    clinic = relationship(
        "Clinic",
        back_populates="doctors"
    )

    # Quan hệ 1 - 1
    # uselist=False để SQLAlchemy biết chỉ có 1 License
    license = relationship(
        "License",
        back_populates="doctor",
        uselist=False
    )


# ==========================
# Bảng License
# Một License chỉ thuộc một Doctor
# ==========================
class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)

    # Số chứng chỉ (không trùng)
    license_number = Column(String(100), unique=True, nullable=False)

    # Cơ quan cấp
    issue_by = Column(String(100), nullable=False)

    # Khóa ngoại
    # unique=True để đảm bảo 1 Doctor chỉ có 1 License
    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        unique=True
    )

    # Quan hệ ngược
    doctor = relationship(
        "Doctor",
        back_populates="license"
    )