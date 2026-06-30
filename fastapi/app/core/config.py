import os
from pathlib import Path
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Hệ thống API Quản lý Sinh viên")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Cấu hình JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret-key-change-it-in-prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    
    # Cấu hình Cơ sở dữ liệu
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "student_db")
    
    # Tự động cấu hình DATABASE_URL nếu chưa được cung cấp
    _db_url = os.getenv("DATABASE_URL")
    if _db_url:
        DATABASE_URL: str = _db_url
    else:
        # Mặc định cấu hình cho MySQL
        DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"

settings = Settings()
