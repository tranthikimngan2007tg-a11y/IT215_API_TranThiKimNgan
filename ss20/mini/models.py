from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    UniqueConstraint,
    CheckConstraint
)

from sqlalchemy.orm import relationship

from database import Base


# =========================================================
# CLASSROOM
# =========================================================

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)

    class_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    class_name = Column(
        String(100),
        nullable=False
    )

    max_students = Column(
        Integer,
        nullable=False,
        default=30
    )

    status = Column(
        String(20),
        nullable=False,
        default="active"
    )

    students = relationship(
        "Student",
        back_populates="classroom"
    )

    __table_args__ = (
        CheckConstraint(
            "max_students > 0",
            name="check_max_students_positive"
        ),
    )


# =========================================================
# STUDENT
# =========================================================

class Student(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_code = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    age = Column(
        Integer,
        nullable=False
    )

    gender = Column(
        String(10),
        nullable=False
    )

    class_id = Column(
        Integer,
        ForeignKey(
            "classrooms.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    classroom = relationship(
        "Classroom",
        back_populates="students"
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="student"
    )


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =========================================================
# USER PROFILE
# =========================================================

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(20),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="profile"
    )


# =========================================================
# COURSE
# =========================================================

class Course(Base):
    __tablename__ = "courses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    course_code = Column(
        String(20),
        unique=True,
        nullable=False
    )

    course_name = Column(
        String(100),
        nullable=False
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="course"
    )


# =========================================================
# ENROLLMENT
# N-N: STUDENT <-> COURSE
# =========================================================

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey(
            "courses.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    student = relationship(
        "Student",
        back_populates="enrollments"
    )

    course = relationship(
        "Course",
        back_populates="enrollments"
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            name="uq_student_course"
        ),
    )