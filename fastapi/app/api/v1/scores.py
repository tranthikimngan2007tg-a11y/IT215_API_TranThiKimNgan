from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.crud import crud_score, crud_student
from app.models.score import Score
from app.schemas.score import ScoreResponse, ScoreDetailResponse, ScoreCreate, ScoreUpdate
from app.schemas.response import APIResponse, MetaResponse
from app.models.user import User, UserRole

router = APIRouter()

class GPAResponse(BaseModel):
    student_id: int = Field(..., description="ID của sinh viên")
    gpa: Optional[float] = Field(None, description="Điểm trung bình tích lũy theo trọng số (thang điểm 10)")
    message: str = Field(..., description="Thông điệp phản hồi từ hệ thống")

# Các thao tác đọc: Xem toàn bộ danh sách điểm giới hạn cho Giảng viên, nhưng xem của sinh viên cụ thể mở cho chính họ.
@router.get("/", response_model=APIResponse[List[ScoreDetailResponse]], summary="Lấy danh sách điểm số toàn hệ thống (Chỉ dành cho Giảng viên)")
def list_scores(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[List[ScoreDetailResponse]]:
    """
    Lấy danh sách tất cả điểm số trong hệ thống. Chỉ dành cho Giảng viên.
    """
    records = crud_score.get_scores(db, skip=skip, limit=limit)
    total_record = db.query(Score).count()

    current_page = (skip // limit) + 1 if limit > 0 else 1
    total_page = (total_record + limit - 1) // limit if limit > 0 else 1

    meta_data = MetaResponse(
        currentPage=current_page,
        pageSize=limit,
        totalPage=total_page,
        totalRecord=total_record
    )

    return APIResponse[List[ScoreDetailResponse]](
        statusCode=status.HTTP_200_OK,
        message="Lấy danh sách điểm số toàn hệ thống thành công.",
        data=records,
        meta=meta_data
    )

@router.get("/student/{student_id}", response_model=APIResponse[List[ScoreResponse]], summary="Lấy danh sách điểm số của một sinh viên cụ thể")
def get_student_scores(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> APIResponse[List[ScoreResponse]]:
    """
    Lấy danh sách toàn bộ các đầu điểm của sinh viên.
    - Giảng viên có quyền xem điểm của bất kỳ sinh viên nào.
    - Sinh viên chỉ được phép tự xem điểm số của bản thân.
    """
    db_student = crud_student.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin sinh viên."
        )
        
    if current_user.role == UserRole.STUDENT:
        if db_student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối. Bạn chỉ có quyền xem điểm số của chính mình."
            )
            
    records = crud_score.get_scores_by_student(db, student_id=student_id)
    return APIResponse[List[ScoreResponse]](
        statusCode=status.HTTP_200_OK,
        message="Lấy danh sách điểm của sinh viên thành công.",
        data=records
    )

@router.get("/student/{student_id}/gpa", response_model=APIResponse[GPAResponse], summary="Tính điểm trung bình tích lũy GPA của sinh viên")
def get_student_gpa(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> APIResponse[GPAResponse]:
    """
    Tính điểm trung bình tích lũy GPA theo trọng số của sinh viên (thang điểm 10).
    - Giảng viên có quyền xem điểm GPA của mọi sinh viên.
    - Sinh viên chỉ có quyền tự xem điểm GPA tích lũy của bản thân.
    """
    db_student = crud_student.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin sinh viên."
        )
        
    if current_user.role == UserRole.STUDENT:
        if db_student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối. Bạn chỉ có quyền xem điểm GPA của chính mình."
            )
            
    gpa = crud_score.calculate_student_gpa(db, student_id=student_id)
    msg = "Tính điểm trung bình GPA thành công." if gpa is not None else "Chưa có thông tin điểm số được ghi nhận cho sinh viên này."
    
    gpa_data = GPAResponse(student_id=student_id, gpa=gpa, message=msg)
    return APIResponse[GPAResponse](
        statusCode=status.HTTP_200_OK,
        message=msg,
        data=gpa_data
    )

# Các thao tác ghi: Chỉ dành cho Giảng viên (LECTURERS)
@router.post("/", response_model=APIResponse[ScoreResponse], status_code=status.HTTP_201_CREATED, summary="Thêm điểm số mới (Chỉ dành cho Giảng viên)")
def add_score(
    score_in: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[ScoreResponse]:
    """
    Nhập một đầu điểm số mới cho sinh viên. Chỉ dành cho Giảng viên.
    """
    student = crud_student.get_student_by_id(db, student_id=score_in.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID sinh viên không tồn tại trên hệ thống."
        )
    new_score = crud_score.create_score(db, obj_in=score_in)
    return APIResponse[ScoreResponse](
        statusCode=status.HTTP_201_CREATED,
        message="Nhập điểm số cho sinh viên thành công.",
        data=new_score
    )

@router.put("/{score_id}", response_model=APIResponse[ScoreResponse], summary="Cập nhật điểm số (Chỉ dành cho Giảng viên)")
def update_score(
    score_id: int,
    score_in: ScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[ScoreResponse]:
    """
    Cập nhật thông tin điểm số đã nhập. Chỉ dành cho Giảng viên.
    """
    db_score = crud_score.get_score_by_id(db, score_id=score_id)
    if not db_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bản ghi điểm số để cập nhật."
        )
    updated_score = crud_score.update_score(db, db_score=db_score, obj_in=score_in)
    return APIResponse[ScoreResponse](
        statusCode=status.HTTP_200_OK,
        message="Cập nhật điểm số thành công.",
        data=updated_score
    )

@router.delete("/{score_id}", response_model=APIResponse[None], summary="Xóa điểm số (Chỉ dành cho Giảng viên)")
def delete_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[None]:
    """
    Xóa một đầu điểm số đã nhập. Chỉ dành cho Giảng viên.
    """
    db_score = crud_score.delete_score(db, score_id=score_id)
    if not db_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bản ghi điểm số để xóa."
        )
    return APIResponse[None](
        statusCode=status.HTTP_200_OK,
        message="Xóa đầu điểm thành công.",
        data=None
    )
