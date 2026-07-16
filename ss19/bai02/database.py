from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Chuỗi kết nối MySQL
DATABASE_URL = "mysql+pymysql://root:123456@localhost/hospital_db"

# Tạo engine kết nối tới MySQL
engine = create_engine(DATABASE_URL)

# Tạo Session để thao tác với database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base để các Model kế thừa
Base = declarative_base()


# Dependency mở và đóng kết nối tự động
def get_db():
    db = SessionLocal()

    try:
        # Trả Session cho API sử dụng
        yield db
    finally:
        # Sau khi API chạy xong sẽ đóng kết nối
        db.close()