from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.score import Score
from app.schemas.score import ScoreCreate, ScoreUpdate

def get_score_by_id(db: Session, score_id: int) -> Optional[Score]:
    """
    Lấy thông tin điểm số theo ID của bản ghi
    """
    return db.query(Score).filter(Score.id == score_id).first()

def get_scores(db: Session, skip: int = 0, limit: int = 100) -> List[Score]:
    """
    Lấy danh sách tất cả các điểm số trong hệ thống có phân trang
    """
    return db.query(Score).offset(skip).limit(limit).all()

def get_scores_by_student(db: Session, student_id: int) -> List[Score]:
    """
    Lấy danh sách điểm số của một sinh viên cụ thể dựa trên ID sinh viên
    """
    return db.query(Score).filter(Score.student_id == student_id).all()

def get_scores_by_subject(db: Session, subject_name: str) -> List[Score]:
    """
    Lấy danh sách điểm số theo tên môn học
    """
    return db.query(Score).filter(Score.subject_name.ilike(subject_name)).all()

def create_score(db: Session, obj_in: ScoreCreate) -> Score:
    """
    Tạo mới một bản ghi điểm số cho sinh viên
    """
    db_score = Score(
        student_id=obj_in.student_id,
        subject_name=obj_in.subject_name,
        score_value=obj_in.score_value,
        weight=obj_in.weight,
        remarks=obj_in.remarks
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

def update_score(db: Session, db_score: Score, obj_in: ScoreUpdate) -> Score:
    """
    Cập nhật thông tin bản ghi điểm số
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_score, field, update_data[field])
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

def delete_score(db: Session, score_id: int) -> Optional[Score]:
    """
    Xóa bản ghi điểm số theo ID
    """
    db_score = get_score_by_id(db, score_id)
    if db_score:
        db.delete(db_score)
        db.commit()
    return db_score

def calculate_student_gpa(db: Session, student_id: int) -> Optional[float]:
    """
    Tính toán điểm trung bình tích lũy GPA theo trọng số của sinh viên.
    Công thức: TỔNG(điểm số * trọng số) / TỔNG(trọng số)
    """
    # Lấy tất cả các điểm số đã ghi nhận của sinh viên
    scores = get_scores_by_student(db, student_id)
    if not scores:
        return None
        
    total_weighted_score = sum(s.score_value * s.weight for s in scores)
    total_weight = sum(s.weight for s in scores)
    
    if total_weight == 0:
        return 0.0
        
    return round(total_weighted_score / total_weight, 2)
