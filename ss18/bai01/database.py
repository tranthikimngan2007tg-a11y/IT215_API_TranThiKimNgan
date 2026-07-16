from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:123456@localhost/workshop_management"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Tạo và đóng kết nối database sau mỗi request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()