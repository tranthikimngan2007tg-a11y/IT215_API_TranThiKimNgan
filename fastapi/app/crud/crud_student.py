from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from datetime import date
from app.models.student import Student
from app.models.user import User, UserRole
from app.models.class_room import ClassRoom
from app.schemas.student import StudentCreate, StudentUpdate, StudentRegister
from app.core.security import get_password_hash

def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """
    Lấy thông tin sinh viên theo ID
    """
    return db.query(Student).filter(Student.id == student_id).first()

def get_student_by_code(db: Session, student_code: str) -> Optional[Student]:
    """
    Lấy thông tin sinh viên theo mã sinh viên (ví dụ: SV1001)
    """
    return db.query(Student).filter(Student.student_code == student_code).first()

def get_student_by_user_id(db: Session, user_id: int) -> Optional[Student]:
    """
    Lấy thông tin sinh viên dựa trên ID tài khoản người dùng liên kết
    """
    return db.query(Student).filter(Student.user_id == user_id).first()

def create_student(db: Session, obj_in: StudentCreate) -> Student:
    """
    Tạo hồ sơ sinh viên mới liên kết với tài khoản người dùng đã có sẵn
    """
    db_student = Student(
        user_id=obj_in.user_id,
        student_code=obj_in.student_code.upper(),
        first_name=obj_in.first_name,
        last_name=obj_in.last_name,
        date_of_birth=obj_in.date_of_birth,
        gender=obj_in.gender,
        phone=obj_in.phone,
        class_id=obj_in.class_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def register_student(db: Session, obj_in: StudentRegister) -> Student:
    """
    Đăng ký tài khoản người dùng đồng thời khởi tạo hồ sơ sinh viên tương ứng trong cùng một transaction.
    Nếu một trong hai bước gặp lỗi, toàn bộ giao dịch sẽ tự động được rollback để đảm bảo tính toàn vẹn dữ liệu.
    """
    # Bước 1: Khởi tạo tài khoản người dùng mới
    hashed_password = get_password_hash(obj_in.password)
    db_user = User(
        username=obj_in.username,
        email=obj_in.email,
        hashed_password=hashed_password,
        role=UserRole.STUDENT,
        is_active=True
    )
    db.add(db_user)
    db.flush()  # Đồng bộ thông tin tạm thời để lấy giá trị db_user.id tự động tạo ra từ Database

    # Bước 2: Tạo hồ sơ sinh viên chi tiết liên kết với ID tài khoản vừa sinh ra
    db_student = Student(
        user_id=db_user.id,
        student_code=obj_in.student_code.upper(),
        first_name=obj_in.first_name,
        last_name=obj_in.last_name,
        date_of_birth=obj_in.date_of_birth,
        gender=obj_in.gender,
        phone=obj_in.phone,
        class_id=obj_in.class_id
    )
    db.add(db_student)
    db.commit()  # Ghi nhận hoàn tất cả hai thực thể vào cơ sở dữ liệu
    db.refresh(db_student)
    return db_student

def update_student(db: Session, db_student: Student, obj_in: StudentUpdate) -> Student:
    """
    Cập nhật thông tin chi tiết hồ sơ sinh viên
    """
    update_data = obj_in.model_dump(exclude_unset=True)
    if "student_code" in update_data:
        update_data["student_code"] = update_data["student_code"].upper()
    for field in update_data:
        setattr(db_student, field, update_data[field])
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int) -> bool:
    """
    Xóa hồ sơ sinh viên. Để tránh dư thừa dữ liệu rác, hệ thống sẽ thực hiện xóa tài khoản User liên kết,
    qua đó cơ chế cascade sẽ tự động xóa sạch hồ sơ sinh viên chi tiết.
    """
    db_student = get_student_by_id(db, student_id)
    if db_student:
        # Tìm và xóa tài khoản người dùng liên kết
        db_user = db.query(User).filter(User.id == db_student.user_id).first()
        if db_user:
            db.delete(db_user)
        else:
            db.delete(db_student)
        db.commit()
        return True
    return False

def search_students_advanced(
    db: Session,
    *,
    search_query: Optional[str] = None,
    class_id: Optional[int] = None,
    gender: Optional[str] = None,
    dob_from: Optional[date] = None,
    dob_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[Student], int]:
    """
    Tìm kiếm nâng cao thông tin sinh viên kết hợp phân trang dữ liệu.
    Hàm này tổng hợp các bộ lọc động, chạy câu truy vấn tối ưu hóa thông qua các SQL Index
    (student_code, first_name, last_name và composite idx_student_name) để tăng tốc độ phản hồi.
    """
    query = db.query(Student)

    # Danh sách lưu trữ các điều kiện lọc động
    filters = []

    if search_query:
        # Áp dụng tìm kiếm tương đối không phân biệt hoa thường dựa trên các cột được đánh index
        q = f"%{search_query}%"
        filters.append(
            or_(
                Student.student_code.ilike(q),
                Student.first_name.ilike(q),
                Student.last_name.ilike(q),
                # Cho phép tìm kiếm gộp theo cả Họ và Tên ghép lại
                func.concat(Student.first_name, " ", Student.last_name).ilike(q)
            )
        )

    if class_id is not None:
        filters.append(Student.class_id == class_id)

    if gender:
        filters.append(Student.gender == gender)

    if dob_from:
        filters.append(Student.date_of_birth >= dob_from)
    
    if dob_to:
        filters.append(Student.date_of_birth <= dob_to)

    if filters:
        query = query.filter(and_(*filters))

    # Tính tổng số sinh viên thỏa mãn điều kiện lọc trước khi thực hiện phân trang
    total_count = query.count()

    # Lấy danh sách kết quả sau phân trang (offset và limit)
    # Sắp xếp mặc định theo mã sinh viên để có thứ tự đồng nhất và tận dụng index có sẵn
    records = query.order_by(Student.student_code).offset(skip).limit(limit).all()

    return records, total_count
