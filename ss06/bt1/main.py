from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class CreateCourse(BaseModel):
    code: str
    name: str = Field(min_length=1)
    duration: int = Field(gt=0)
    fee: float = Field(ge=0)

courses = [
    {"id": 1, "code": "PY101", "name": "Python Basic", "duration": 30, "fee": 3000000},
    {"id": 2, "code": "API101", "name": "FastAPI Basic", "duration": 24, "fee": 2500000},
    {"id": 3, "code": "JV101", "name": "Java Basic", "duration": 40, "fee": 4000000}
]

@app.get("/courses")
def get_courses(
    keyword: Optional[str] = None,
    min_fee: Optional[float] = None,
    max_fee: Optional[float] = None
):
    result = courses

    if keyword:
        keyword = keyword.lower()
        result = [
            course for course in result
            if keyword in course["code"].lower()
            or keyword in course["name"].lower()
        ]

    if min_fee is not None:
        result = [
            course for course in result
            if course["fee"] >= min_fee
        ]

    if max_fee is not None:
        result = [
            course for course in result
            if course["fee"] <= max_fee
        ]

    return result


@app.get("/courses/{course_id}")
def get_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course

    raise HTTPException(
        status_code=404,
        detail="Course not found"
    )


@app.post("/courses")
def create_course(course: CreateCourse):
    for cour in courses:
        if cour["code"] == course.code:
            raise HTTPException(
                status_code=409,
                detail="Course code already exists"
            )

    max_id = 0

    for cour in courses:
        if cour["id"] > max_id:
            max_id = cour["id"]

    new_course = {
        "id": max_id + 1,
        "code": course.code,
        "name": course.name,
        "duration": course.duration,
        "fee": course.fee
    }

    courses.append(new_course)

    return new_course


@app.put("/courses/{course_id}")
def update_course(course_id: int, course: CreateCourse):
    for cour in courses:
        if cour["code"] == course.code and cour["id"] != course_id:
            raise HTTPException(
                status_code=409,
                detail="Course code already exists"
            )

    for cour in courses:
        if cour["id"] == course_id:
            cour["code"] = course.code
            cour["name"] = course.name
            cour["duration"] = course.duration
            cour["fee"] = course.fee
            return cour

    raise HTTPException(
        status_code=404,
        detail="Course not found"
    )


@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            courses.remove(course)
            return {
                "message": "Delete successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Course not found"
    )