from database import engine, Base
import hospital_models

Base.metadata.create_all(bind=engine)

print("Tạo bảng thành công!")