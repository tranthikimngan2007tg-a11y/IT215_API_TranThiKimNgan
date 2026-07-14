from sqlalchemy import Column, String, Integer, Float, CheckConstraint
from database import Base

class CrudModel(Base):
    __tablename__ = "curd"

    id = Column(String(30), primary_key=True)
    category = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    rental_rate = Column(Float,)