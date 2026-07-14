from schema import TeamRequestDTO
from sqlalchemy.orm import Session
from models import TeamModel
from sqlalchemy.exc import SQLAlchemyError

def get_all_team(db: Session):
    return db.query(TeamModel).all()