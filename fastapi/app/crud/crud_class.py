from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.class_room import ClassRoom
from app.schemas.class_room import ClassRoomCreate, ClassRoomUpdate

def get_class_by_id(db: Session, class_id: int) -> Optional[ClassRoom]:
    """
    Lấy thông tin lớp học theo ID
    """
    return db.query(ClassRoom).filter(ClassRoom.id == class_id).first()

def get_class_by_code(db: Session, class_code: str) -> Optional[ClassRoom]:
    """
    Lấy thông tin lớp học theo mã lớp học (ví dụ: JV2403)
    """
    return db.query(ClassRoom).filter(ClassRoom.class_code == class_code).first()

def get_classes(db: Session, skip: int = 0, limit: int = 100) -> List[ClassRoom]:
    """
    Lấy danh sách các lớp học có phân trang
    """
    return db.query(ClassRoom).offset(skip).limit(limit).all()

def create_class(db: Session, obj_in: ClassRoomCreate) -> ClassRoom:
    """
    Tạo một lớp học mới (tự động chuyển mã lớp học sang chữ in hoa)
    """
    db_class = ClassRoom(
        class_code=obj_in.class_code.upper(),  # Bắt buộc chuyển mã lớp sang in hoa
        name=obj_in.name,
        description=obj_in.description
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def update_class(db: Session, db_class: ClassRoom, obj_in: ClassRoomUpdate) -> ClassRoom:
    """
    Cập nhật thông tin chi tiết lớp học
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    if "class_code" in update_data:
        update_data["class_code"] = update_data["class_code"].upper()
    for field in update_data:
        setattr(db_class, field, update_data[field])
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def delete_class(db: Session, class_id: int) -> Optional[ClassRoom]:
    """
    Xóa một lớp học dựa trên ID lớp học
    """
    db_class = get_class_by_id(db, class_id)
    if db_class:
        db.delete(db_class)
        db.commit()
    return db_class
