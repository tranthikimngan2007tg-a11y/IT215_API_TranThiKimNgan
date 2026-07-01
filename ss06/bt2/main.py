from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class CreateStudent(BaseModel):
    code: str
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    age: int = Field(gt=0)

students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]

@app.get("/students")
def get_students(
    keyword: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
):
    result = students

    if keyword:
        keyword = keyword.lower()
        result = [
            student for student in result
            if keyword in student["code"].lower()
            or keyword in student["name"].lower()
            or keyword in student["email"].lower()
        ]

    if min_age is not None:
        result = [
            student for student in result
            if student["age"] >= min_age
        ]

    if max_age is not None:
        result = [
            student for student in result
            if student["age"] <= max_age
        ]

    return result


@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


@app.post("/students")
def create_student(student: CreateStudent):
    for stu in students:
        if stu["code"] == student.code:
            raise HTTPException(
                status_code=409,
                detail="Student code already exists"
            )

    max_id = 0

    for stu in students:
        if stu["id"] > max_id:
            max_id = stu["id"]

    new_student = {
        "id": max_id + 1,
        "code": student.code,
        "name": student.name,
        "email": student.email,
        "age": student.age
    }

    students.append(new_student)

    return new_student


@app.put("/students/{student_id}")
def update_student(student_id: int, student: CreateStudent):
    for stu in students:
        if stu["code"] == student.code and stu["id"] != student_id:
            raise HTTPException(
                status_code=409,
                detail="Student code already exists"
            )

    for stu in students:
        if stu["id"] == student_id:
            stu["code"] = student.code
            stu["name"] = student.name
            stu["email"] = student.email
            stu["age"] = student.age
            return stu

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            students.remove(student)
            return {
                "message": "Delete successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )