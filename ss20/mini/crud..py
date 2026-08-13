from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from models import Classroom, Student
from schemas import StudentCreate, StudentUpdate


# =========================================================
# GET STUDENTS
# =========================================================

def get_students(
    db: Session,
    search: str | None = None,
    class_id: int | None = None
):
    query = (
        db.query(Student)
        .options(joinedload(Student.classroom))
    )

    if search:
        keyword = f"%{search}%"

        query = query.filter(
            or_(
                Student.full_name.like(keyword),
                Student.student_code.like(keyword),
                Student.email.like(keyword)
            )
        )

    if class_id is not None:
        query = query.filter(
            Student.class_id == class_id
        )

    return query.order_by(Student.id.asc()).all()


# =========================================================
# GET STUDENT BY ID
# =========================================================

def get_student_by_id(
    db: Session,
    student_id: int
):
    return (
        db.query(Student)
        .options(joinedload(Student.classroom))
        .filter(Student.id == student_id)
        .first()
    )


# =========================================================
# CHECK CLASSROOM
# =========================================================

def get_classroom_by_id(
    db: Session,
    class_id: int
):
    return (
        db.query(Classroom)
        .filter(Classroom.id == class_id)
        .first()
    )


# =========================================================
# CHECK STUDENT CODE
# =========================================================

def get_student_by_code(
    db: Session,
    student_code: str
):
    return (
        db.query(Student)
        .filter(Student.student_code == student_code)
        .first()
    )


# =========================================================
# CHECK EMAIL
# =========================================================

def get_student_by_email(
    db: Session,
    email: str
):
    return (
        db.query(Student)
        .filter(Student.email == email)
        .first()
    )


# =========================================================
# COUNT STUDENTS IN CLASS
# =========================================================

def count_students_in_class(
    db: Session,
    class_id: int
):
    return (
        db.query(Student)
        .filter(Student.class_id == class_id)
        .count()
    )


# =========================================================
# CREATE STUDENT
# =========================================================

def create_student(
    db: Session,
    student_data: StudentCreate
):
    classroom = get_classroom_by_id(
        db,
        student_data.class_id
    )

    if classroom is None:
        raise ValueError("Lớp học không tồn tại")

    if classroom.status != "active":
        raise ValueError(
            "Lớp học hiện không hoạt động"
        )

    current_students = count_students_in_class(
        db,
        classroom.id
    )

    if current_students >= classroom.max_students:
        raise ValueError(
            "Lớp học đã đủ số lượng sinh viên"
        )

    existing_code = get_student_by_code(
        db,
        student_data.student_code
    )

    if existing_code:
        raise ValueError(
            "Mã sinh viên đã tồn tại"
        )

    existing_email = get_student_by_email(
        db,
        str(student_data.email)
    )

    if existing_email:
        raise ValueError(
            "Email đã tồn tại"
        )

    student = Student(
        student_code=student_data.student_code,
        full_name=student_data.full_name,
        email=str(student_data.email),
        age=student_data.age,
        gender=student_data.gender,
        class_id=student_data.class_id
    )

    db.add(student)
    db.commit()

    db.refresh(student)

    return get_student_by_id(
        db,
        student.id
    )


# =========================================================
# UPDATE STUDENT
# =========================================================

def update_student(
    db: Session,
    student_id: int,
    student_data: StudentUpdate
):
    student = get_student_by_id(
        db,
        student_id
    )

    if student is None:
        raise LookupError(
            "Không tìm thấy sinh viên"
        )

    update_data = student_data.model_dump(
        exclude_unset=True
    )

    # -----------------------------------------------------
    # CHECK STUDENT CODE
    # -----------------------------------------------------

    if "student_code" in update_data:
        existing_code = (
            db.query(Student)
            .filter(
                Student.student_code
                == update_data["student_code"],
                Student.id != student_id
            )
            .first()
        )

        if existing_code:
            raise ValueError(
                "Mã sinh viên đã tồn tại"
            )

    # -----------------------------------------------------
    # CHECK EMAIL
    # -----------------------------------------------------

    if "email" in update_data:
        existing_email = (
            db.query(Student)
            .filter(
                Student.email
                == str(update_data["email"]),
                Student.id != student_id
            )
            .first()
        )

        if existing_email:
            raise ValueError(
                "Email đã tồn tại"
            )

    # -----------------------------------------------------
    # CHECK CLASS WHEN CHANGE CLASS
    # -----------------------------------------------------

    if "class_id" in update_data:

        new_class_id = update_data["class_id"]

        if new_class_id != student.class_id:

            new_class = get_classroom_by_id(
                db,
                new_class_id
            )

            if new_class is None:
                raise ValueError(
                    "Lớp học mới không tồn tại"
                )

            if new_class.status != "active":
                raise ValueError(
                    "Lớp học mới không hoạt động"
                )

            current_students = count_students_in_class(
                db,
                new_class_id
            )

            if current_students >= new_class.max_students:
                raise ValueError(
                    "Lớp học mới đã đủ số lượng sinh viên"
                )

    # -----------------------------------------------------
    # UPDATE DATA
    # -----------------------------------------------------

    for key, value in update_data.items():

        if key == "email":
            value = str(value)

        setattr(student, key, value)

    db.commit()

    db.refresh(student)

    return get_student_by_id(
        db,
        student.id
    )