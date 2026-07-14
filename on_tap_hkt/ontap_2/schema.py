from pydantic import BaseModel

class TeamRequestDTO(BaseModel):
    country_name = str,
    coach_name = str,
    group_name = str