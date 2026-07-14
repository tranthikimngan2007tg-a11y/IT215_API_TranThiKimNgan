from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_code = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), index=True, nullable=False)
    last_name = Column(String(100), index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Mối quan hệ liên kết bảng
    user = relationship("User", back_populates="student_profile")
    classroom = relationship("ClassRoom", back_populates="students")
    scores = relationship("Score", back_populates="student", cascade="all, delete-orphan")

    # Định nghĩa các index bổ sung để tối ưu hóa truy vấn tìm kiếm nâng cao.
    # index=True ở cấp độ cột đã tạo index đơn. Ta tạo thêm Composite Index để hỗ trợ tìm kiếm theo họ & tên kết hợp.
    __table_args__ = (
        Index("idx_student_name", "first_name", "last_name"),
    )
