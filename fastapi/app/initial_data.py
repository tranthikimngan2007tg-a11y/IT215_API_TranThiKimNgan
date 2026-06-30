from sqlalchemy.orm import Session
from datetime import date

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.class_room import ClassRoom
from app.models.student import Student
from app.models.score import Score
from app.core.security import get_password_hash
from app.crud import crud_user, crud_student, crud_class, crud_score
from app.schemas.student import StudentRegister

def init_db(db: Session) -> None:
    # 1. Khởi tạo/kiểm tra các bảng dữ liệu
    Base.metadata.create_all(bind=engine)
    print("Database: Kiểm tra và khởi tạo các bảng hoàn tất.")

    # 2. Kiểm tra xem giảng viên mặc định đã tồn tại hay chưa
    lecturer_username = "teacher_smith"
    db_lecturer = crud_user.get_user_by_username(db, username=lecturer_username)
    if not db_lecturer:
        print(f"Đang khởi tạo Giảng viên mặc định: {lecturer_username} ...")
        new_lecturer = User(
            username=lecturer_username,
            email="smith@school.edu",
            hashed_password=get_password_hash("password123"),
            role=UserRole.LECTURER,
            is_active=True
        )
        db.add(new_lecturer)
        db.commit()
        db.refresh(new_lecturer)
        print("Tạo tài khoản Giảng viên mặc định thành công (Tài khoản: teacher_smith, Mật khẩu: password123)")
    else:
        print("Tài khoản Giảng viên mặc định đã tồn tại.")

    # 3. Tạo lớp học mặc định thứ nhất
    class_code = "JV2403"
    db_class = db.query(ClassRoom).filter(ClassRoom.class_code == class_code).first()
    if not db_class:
        print(f"Đang tạo lớp học: {class_code} ...")
        db_class = ClassRoom(
            class_code=class_code,
            name="Java Backend Development 2024",
            description="Lớp học lập trình chuyên sâu Java Fullstack & Backend Bootcamp 2024"
        )
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
        print("Tạo lớp học mặc định thứ nhất thành công.")
    else:
        print("Lớp học mặc định thứ nhất đã tồn tại.")

    # 4. Tạo thêm một lớp học thứ hai để phục vụ kiểm thử tìm kiếm
    class_code_py = "PY2404"
    db_class_py = db.query(ClassRoom).filter(ClassRoom.class_code == class_code_py).first()
    if not db_class_py:
        print(f"Đang tạo lớp học: {class_code_py} ...")
        db_class_py = ClassRoom(
            class_code=class_code_py,
            name="Python Backend & FastAPI 2024",
            description="Lớp học chuyên sâu lập trình Python và Web Framework FastAPI"
        )
        db.add(db_class_py)
        db.commit()
        db.refresh(db_class_py)
        print("Tạo lớp học Python thành công.")
    else:
        print("Lớp học Python đã tồn tại.")

    # 5. Khởi tạo tài khoản và hồ sơ sinh viên mặc định thứ nhất (Alice)
    student_username = "alice_green"
    db_student_user = crud_user.get_user_by_username(db, username=student_username)
    if not db_student_user:
        print(f"Đang đăng ký Sinh viên: {student_username} ...")
        student_in = StudentRegister(
            username=student_username,
            email="alice@school.edu",
            password="password123",
            student_code="SV1001",
            first_name="Alice",
            last_name="Green",
            date_of_birth=date(2002, 5, 15),
            gender="Female",
            phone="0912345678",
            class_id=db_class.id
        )
        db_student = crud_student.register_student(db, obj_in=student_in)
        print("Đăng ký tài khoản sinh viên Alice thành công (Tài khoản: alice_green, Mật khẩu: password123, Mã SV: SV1001)")
    else:
        print("Sinh viên Alice đã tồn tại.")
        db_student = db.query(Student).filter(Student.user_id == db_student_user.id).first()

    # 6. Khởi tạo sinh viên thứ hai để kiểm thử tìm kiếm nâng cao (Bob)
    student_username_bob = "bob_jones"
    db_student_user_bob = crud_user.get_user_by_username(db, username=student_username_bob)
    if not db_student_user_bob:
        print(f"Đang đăng ký Sinh viên: {student_username_bob} ...")
        student_in_bob = StudentRegister(
            username=student_username_bob,
            email="bob@school.edu",
            password="password123",
            student_code="SV1002",
            first_name="Bob",
            last_name="Jones",
            date_of_birth=date(2001, 10, 22),
            gender="Male",
            phone="0987654321",
            class_id=db_class_py.id
        )
        db_student_bob = crud_student.register_student(db, obj_in=student_in_bob)
        print("Đăng ký tài khoản sinh viên Bob thành công (Tài khoản: bob_jones, Mật khẩu: password123, Mã SV: SV1002)")
    else:
        print("Sinh viên Bob đã tồn tại.")
        db_student_bob = db.query(Student).filter(Student.user_id == db_student_user_bob.id).first()

    # 7. Thêm các đầu điểm số mẫu cho sinh viên thứ nhất
    if db_student:
        existing_scores = db.query(Score).filter(Score.student_id == db_student.id).all()
        if not existing_scores:
            print("Đang thêm điểm số mẫu cho sinh viên Alice...")
            scores_to_add = [
                Score(student_id=db_student.id, subject_name="Math", score_value=8.5, weight=0.3, remarks="Tiến bộ tốt ở bài giữa kỳ"),
                Score(student_id=db_student.id, subject_name="Math", score_value=9.0, weight=0.7, remarks="Làm bài thi cuối kỳ xuất sắc"),
                Score(student_id=db_student.id, subject_name="Python Backend", score_value=9.5, weight=1.0, remarks="Hoàn thành các bài tập lớn xuất sắc")
            ]
            db.bulk_save_objects(scores_to_add)
            db.commit()
            print("Đã thêm điểm số mẫu cho sinh viên Alice thành công.")
            
    # 8. Thêm các đầu điểm số mẫu cho sinh viên thứ hai
    if db_student_bob:
        existing_scores_bob = db.query(Score).filter(Score.student_id == db_student_bob.id).all()
        if not existing_scores_bob:
            print("Đang thêm điểm số mẫu cho sinh viên Bob...")
            scores_to_add_bob = [
                Score(student_id=db_student_bob.id, subject_name="Math", score_value=6.5, weight=0.3, remarks="Kiểm tra giữa kỳ đạt yêu cầu"),
                Score(student_id=db_student_bob.id, subject_name="Math", score_value=7.2, weight=0.7, remarks="Thi cuối kỳ đạt điểm khá"),
                Score(student_id=db_student_bob.id, subject_name="Python Backend", score_value=8.0, weight=1.0, remarks="Hoàn thành đầy đủ các đồ án được giao")
            ]
            db.bulk_save_objects(scores_to_add_bob)
            db.commit()
            print("Đã thêm điểm số mẫu cho sinh viên Bob thành công.")

def main() -> None:
    print("Bắt đầu quá trình nạp dữ liệu mẫu vào Cơ sở dữ liệu...")
    db = SessionLocal()
    try:
        init_db(db)
        print("Hoàn tất quá trình seeding dữ liệu.")
    except Exception as e:
        print(f"Gặp lỗi khi đang seeding dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
