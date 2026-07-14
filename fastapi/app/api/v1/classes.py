from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.core.database import get_db
from app.crud import crud_class
from app.models.class_room import ClassRoom
from app.schemas.class_room import ClassRoomResponse, ClassRoomCreate, ClassRoomUpdate
from app.schemas.response import APIResponse, MetaResponse
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=APIResponse[List[ClassRoomResponse]], summary="Lấy danh sách tất cả các lớp học")
def list_classes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user)
) -> APIResponse[List[ClassRoomResponse]]:
    """
    Lấy danh sách các lớp học hiện có trong hệ thống (Hỗ trợ phân trang).
    """
    records = crud_class.get_classes(db, skip=skip, limit=limit)
    total_record = db.query(ClassRoom).count()
    
    current_page = (skip // limit) + 1 if limit > 0 else 1
    total_page = (total_record + limit - 1) // limit if limit > 0 else 1

    meta_data = MetaResponse(
        currentPage=current_page,
        pageSize=limit,
        totalPage=total_page,
        totalRecord=total_record
    )

    return APIResponse[List[ClassRoomResponse]](
        statusCode=status.HTTP_200_OK,
        message="Lấy danh sách lớp học thành công.",
        data=records,
        meta=meta_data
    )

@router.get("/{class_id}", response_model=APIResponse[ClassRoomResponse], summary="Lấy thông tin lớp học theo ID")
def get_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(deps.get_current_active_user)
) -> APIResponse[ClassRoomResponse]:
    """
    Lấy thông tin chi tiết của một lớp học dựa trên ID.
    """
    db_class = crud_class.get_class_by_id(db, class_id=class_id)
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin lớp học."
        )
    return APIResponse[ClassRoomResponse](
        statusCode=status.HTTP_200_OK,
        message="Lấy thông tin chi tiết lớp học thành công.",
        data=db_class
    )

@router.post(
    "/", 
    response_model=APIResponse[ClassRoomResponse], 
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mới một lớp học (Chỉ dành cho Giảng viên)"
)
def create_new_class(
    class_in: ClassRoomCreate,
    db: Session = Depends(get_db),
    current_user = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[ClassRoomResponse]:
    """
    Khởi tạo một lớp học mới. Yêu cầu quyền Giảng viên.
    """
    db_class = crud_class.get_class_by_code(db, class_code=class_in.class_code)
    if db_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã lớp học đã tồn tại trong hệ thống."
        )
    new_class = crud_class.create_class(db, obj_in=class_in)
    return APIResponse[ClassRoomResponse](
        statusCode=status.HTTP_201_CREATED,
        message="Tạo mới lớp học thành công.",
        data=new_class
    )

@router.put("/{class_id}", response_model=APIResponse[ClassRoomResponse], summary="Cập nhật thông tin lớp học (Chỉ dành cho Giảng viên)")
def update_classroom(
    class_id: int,
    class_in: ClassRoomUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[ClassRoomResponse]:
    """
    Cập nhật thông tin chi tiết lớp học theo ID. Yêu cầu quyền Giảng viên.
    """
    db_class = crud_class.get_class_by_id(db, class_id=class_id)
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin lớp học."
        )
    
    if class_in.class_code:
        existing = crud_class.get_class_by_code(db, class_code=class_in.class_code)
        if existing and existing.id != class_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã lớp học cập nhật trùng với mã lớp đã tồn tại."
            )
            
    updated_class = crud_class.update_class(db, db_class=db_class, obj_in=class_in)
    return APIResponse[ClassRoomResponse](
        statusCode=status.HTTP_200_OK,
        message="Cập nhật thông tin lớp học thành công.",
        data=updated_class
    )

@router.delete("/{class_id}", response_model=APIResponse[ClassRoomResponse], summary="Xóa lớp học (Chỉ dành cho Giảng viên)")
def delete_classroom(
    class_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(deps.RoleChecker([UserRole.LECTURER]))
) -> APIResponse[ClassRoomResponse]:
    """
    Xóa một lớp học dựa trên ID. Yêu cầu quyền Giảng viên.
    """
    db_class = crud_class.get_class_by_id(db, class_id=class_id)
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin lớp học để xóa."
        )
    deleted_class = crud_class.delete_class(db, class_id=class_id)
    return APIResponse[ClassRoomResponse](
        statusCode=status.HTTP_200_OK,
        message="Xóa lớp học thành công.",
        data=deleted_class
    )
