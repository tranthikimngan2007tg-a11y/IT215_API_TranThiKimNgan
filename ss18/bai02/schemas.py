from pydantic import BaseModel
from datetime import datetime


# ==========================
# Student
# ==========================

class StudentCreate(BaseModel):
    student_code: str
    full_name: str
    email: str
    status: str


class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: str
    status: str

    class Config:
        from_attributes = True


# ==========================
# Workshop
# ==========================

class WorkshopCreate(BaseModel):
    title: str
    description: str
    maximum_participants: int
    status: str
    start_time: datetime


class WorkshopResponse(BaseModel):
    id: int
    title: str
    description: str
    maximum_participants: int
    status: str
    start_time: datetime

    class Config:
        from_attributes = True


# ==========================
# Registration
# ==========================

class RegistrationCreate(BaseModel):
    student_id: int
    workshop_id: int


class RegistrationResponse(BaseModel):
    id: int
    student_id: int
    workshop_id: int
    registered_at: datetime
    status: str

    class Config:
        from_attributes = True


# ==========================
# API:
# GET /students/{id}/workshops
# ==========================

class WorkshopInfo(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class StudentWorkshopsResponse(BaseModel):
    student_id: int
    full_name: str
    workshops: list[WorkshopInfo]


# ==========================
# API:
# GET /workshops/{id}/students
# ==========================

class StudentInfo(BaseModel):
    id: int
    full_name: str

    class Config:
        from_attributes = True


class WorkshopStudentsResponse(BaseModel):
    workshop_id: int
    title: str
    students: list[StudentInfo]