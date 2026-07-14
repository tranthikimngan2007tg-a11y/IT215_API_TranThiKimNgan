from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentBase(BaseModel):
    full_name: str
    email: EmailStr
    major: str
    gpa: float


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    major: Optional[str] = None
    gpa: Optional[float] = None


class StudentResponse(StudentBase):
    id: int

    model_config = {"from_attributes": True}
