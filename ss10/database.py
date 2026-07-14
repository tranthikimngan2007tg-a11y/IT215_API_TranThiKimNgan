# file chỉ dùng để cấu hình kết nối database
# dùng thư viện sqlalchemy giúp kết nối với mysql
# tải thư viện về - pip install sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
# bước 1: cấu hình connection tới database
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/school_db"

# bước 2: tạo engine điều phối kết nối vật lý(connection pool)
engine = create_engine(DATABASE_URL)

# bước 3: tạo ra localsession để gửi dữ liệu
Localsession = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)
Base = declarative_base()
# bước 4: tạo hàm để gọi dữ liệu khởi chạy
def get_db():
    try:
        db = Localsession()
        yield db
    finally:
        db.close()
