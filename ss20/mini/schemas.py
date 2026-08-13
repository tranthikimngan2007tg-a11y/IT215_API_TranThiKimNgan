from typing import Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


# =========================================================
# CLASSROOM RESPONSE
# =========================================================

class ClassroomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    class_code: str
    class_name: str
    max_students: int
    status: str


# =========================================================
# STUDENT CREATE
# =========================================================

class StudentCreate(BaseModel):
    student_code: str = Field(
        ...,
        min_length=3,
        max_length=20
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    age: int = Field(
        ...,
        ge=16,
        le=60
    )

    gender: str

    class_id: int = Field(
        ...,
        ge=1
    )

    @field_validator("student_code", "full_name")
    @classmethod
    def strip_text(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Không được để trống")

        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str):
        value = value.lower().strip()

        allowed = ["male", "female", "other"]

        if value not in allowed:
            raise ValueError(
                "gender phải là male, female hoặc other"
            )

        return value


# =========================================================
# STUDENT UPDATE
# =========================================================

class StudentUpdate(BaseModel):
    student_code: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=20
    )

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None

    age: Optional[int] = Field(
        default=None,
        ge=16,
        le=60
    )

    gender: Optional[str] = None

    class_id: Optional[int] = Field(
        default=None,
        ge=1
    )

    @field_validator("student_code", "full_name")
    @classmethod
    def strip_text(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Không được để trống")

        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):
        if value is None:
            return value

        value = value.lower().strip()

        allowed = ["male", "female", "other"]

        if value not in allowed:
            raise ValueError(
                "gender phải là male, female hoặc other"
            )

        return value


# =========================================================
# STUDENT RESPONSE
# =========================================================

class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_code: str
    full_name: str
    email: EmailStr
    age: int
    gender: str
    class_id: int
    classroom: ClassroomResponse


# =========================================================
# STANDARD API RESPONSE
# =========================================================

class APIResponse(BaseModel):
    statusCode: int
    message: str
    data: Any
    error: Any
    timestamp: str
    path: str