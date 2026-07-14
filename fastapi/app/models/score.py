from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_name = Column(String(100), index=True, nullable=False)
    score_value = Column(Float, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)  # Hệ số điểm, ví dụ: 0.1 cho kiểm tra miệng, 0.3 cho giữa kỳ, 0.6 cho cuối kỳ
    remarks = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Mối quan hệ liên kết bảng với Sinh viên
    student = relationship("Student", back_populates="scores")

    # Composite Index tối ưu hóa việc truy vấn điểm số theo từng môn học của sinh viên
    __table_args__ = (
        Index("idx_student_subject", "student_id", "subject_name"),
    )
