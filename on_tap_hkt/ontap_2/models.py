from database import Base
from sqlalchemy import String, Integer, Column

class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    country_name = Column(String(100), nullable=False)
    coach_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)

    