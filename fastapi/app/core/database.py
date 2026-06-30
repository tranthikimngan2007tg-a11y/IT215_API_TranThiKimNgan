from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Xác định xem đang sử dụng SQLite hay MySQL
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# SQLite yêu cầu cấu hình kết nối bổ sung
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    # Cấu hình Pool giúp MySQL duy trì kết nối ổn định không bị ngắt
    pool_pre_ping=True if not is_sqlite else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency để khởi tạo và đóng phiên kết nối cơ sở dữ liệu (db session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
