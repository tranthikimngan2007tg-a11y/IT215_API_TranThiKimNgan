from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.crud import crud_student, crud_user, crud_class
from app.schemas.student import StudentResponse, StudentDetailResponse, StudentCreate, StudentUpdate
from app.schemas.response import APIResponse, MetaResponse
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/search", response_model=APIResponse[List[StudentDetailResponse]], summary="Tìm kiếm nâng cao & phân trang hồ sơ sinh viên")
def search_students(
    search_query: Optional[str] = None,
    class_id: Optional[int] = None,
    gender: Optional[str] = None,
    dob_from: Optional[date] = None,
    dob_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> APIResponse[List[StudentDetailResponse]]:
    """
    Tìm kiếm sinh viên với các bộ lọc nâng cao. 
    Hệ thống tối ưu hóa tốc độ tìm kiếm bằng cách sử dụng các SQL Index trên cột tìm kiếm chính.
    """
    records, total = crud_student.search_students_advanced(
        db,
        search_query=search_query,
        class_id=class_id,
        gender=gender,
        dob_from=dob_from,
        dob_to=dob_to,
        skip=skip,
        limit=limit
    )

    current_page = (skip // limit) + 1 if limit > 0 else 1
    total_page = (total + limit - 1) // limit if limit > 0 else 1

    meta_data = MetaResponse(
        currentPage=current_page,
        pageSize=limit,
        totalPage=total_page,
        totalRecord=total
    )

    return APIResponse[List[StudentDetailResponse]](
        statusCode=status.HTTP_200_OK,
        message="Tìm kiếm danh sách sinh viên thành công.",
        data=records,
        meta=meta_data
    )

@router.get("/{student_id}", response_model=APIResponse[StudentDetailResponse], summary="Lấy chi tiết hồ sơ sinh viên theo ID")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> APIResponse[StudentDetailResponse]:
    """
    Lấy thông tin hồ sơ sinh viên theo ID.
    - Giảng viên có quyền xem hồ sơ của bất kỳ sinh viên nào.
    - Sinh viên chỉ có quyền xem hồ sơ của chính mình.
    """
    db_student = crud_student.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin sinh viên."
        )
        
    # Áp dụng kiểm tra vai trò người dùng truy cập
    if current_user.role == UserRole.STUDENT:
        if db_student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối. Bạn chỉ được phép xem thông tin hồ sơ của chính mình."
            )
            
    return APIResponse[StudentDetailResponse](
        statusCode=status.HTTP_200_OK,
        message="Lấy chi tiết hồ sơ sinh viên thành công.",
        data=db_student
    )

@router.post("/", response_model=APIResponse[StudentResponse], status_code=status.HTTP_201_CREATED, summary="Tạo mới hồ sơ sinh viên (Chỉ dành cho Giảng viên)")
def create_new_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[StudentResponse]:
    """
    Tạo trực tiếp thông tin hồ sơ sinh viên liên kết với một ID tài khoản đã có sẵn.
    Chỉ dành cho Giảng viên.
    """
    user = crud_user.get_user_by_id(db, user_id=student_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID tài khoản người dùng không tồn tại."
        )
    if user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản liên kết phải có vai trò 'student' mới được tạo hồ sơ sinh viên."
        )
    
    # Kiểm tra xem tài khoản này đã được liên kết với hồ sơ sinh viên nào chưa
    existing_user_profile = crud_student.get_student_by_user_id(db, user_id=student_in.user_id)
    if existing_user_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hồ sơ sinh viên đã tồn tại cho tài khoản người dùng này."
        )
        
    existing_code = crud_student.get_student_by_code(db, student_code=student_in.student_code)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã sinh viên đã tồn tại trên hệ thống."
        )
        
    if student_in.class_id is not None:
        db_class = crud_class.get_class_by_id(db, class_id=student_in.class_id)
        if not db_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy lớp học."
            )
            
    new_student = crud_student.create_student(db, obj_in=student_in)
    return APIResponse[StudentResponse](
        statusCode=status.HTTP_201_CREATED,
        message="Khởi tạo thông tin sinh viên thành công.",
        data=new_student
    )

@router.put("/{student_id}", response_model=APIResponse[StudentResponse], summary="Cập nhật thông tin hồ sơ sinh viên")
def update_student_profile(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> APIResponse[StudentResponse]:
    """
    Cập nhật thông tin hồ sơ sinh viên.
    - Giảng viên có quyền cập nhật cho mọi sinh viên.
    - Sinh viên chỉ được phép tự cập nhật thông tin của chính mình.
    """
    db_student = crud_student.get_student_by_id(db, student_id=student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin hồ sơ sinh viên."
        )
        
    # Áp dụng kiểm soát truy cập
    if current_user.role == UserRole.STUDENT:
        if db_student.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối. Bạn chỉ được phép tự cập nhật hồ sơ của chính mình."
            )
            
    if student_in.student_code:
        existing = crud_student.get_student_by_code(db, student_code=student_in.student_code)
        if existing and existing.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã sinh viên cập nhật đã được sử dụng bởi sinh viên khác."
            )
            
    if student_in.class_id is not None:
        db_class = crud_class.get_class_by_id(db, class_id=student_in.class_id)
        if not db_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy lớp học."
            )
            
    updated_student = crud_student.update_student(db, db_student=db_student, obj_in=student_in)
    return APIResponse[StudentResponse](
        statusCode=status.HTTP_200_OK,
        message="Cập nhật thông tin hồ sơ sinh viên thành công.",
        data=updated_student
    )

@router.delete("/{student_id}", response_model=APIResponse[None], summary="Xóa hồ sơ sinh viên (Chỉ dành cho Giảng viên)")
def delete_student_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[None]:
    """
    Xóa hồ sơ sinh viên và tài khoản người dùng tương ứng.
    Chỉ dành cho Giảng viên.
    """
    deleted = crud_student.delete_student(db, student_id=student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ sinh viên để xóa."
        )
    return APIResponse[None](
        statusCode=status.HTTP_200_OK,
        message="Xóa thông tin sinh viên thành công.",
        data=None
    )
