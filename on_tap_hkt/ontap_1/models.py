from sqlalchemy import Column, String, Integer
from database import Base


class BookModel(Base):
    __tablename__ = "book_manager"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    isbn = Column(String(50), nullable=False, unique=True)
    status = Column(String(100), default="Available")
    