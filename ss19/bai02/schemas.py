from pydantic import BaseModel
from typing import Optional

class ClinicCreate(BaseModel):
    clinic_name: str
    specialty: str

class DoctorResponse(BaseModel):
    id: int
    doctor_code: str
    salary: float

    class Config:
        from_attributes = True


class DoctorUpdate(BaseModel):
    doctor_code: Optional[str] = None
    salary: Optional[float] = None
    clinic_id: Optional[int] = None

class ClinicDetailResponse(BaseModel):
    id: int
    clinic_name: str
    specialty: str

    # Danh sách Doctor thuộc Clinic
    doctors: list[DoctorResponse]

    class Config:
        from_attributes = True

class LicenseResponse(BaseModel):
    id: int
    license_number: str
    issue_by: str
    doctor_id: int

    class Config:
        from_attributes = True