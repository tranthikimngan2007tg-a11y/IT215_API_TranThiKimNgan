from pydantic import BaseModel

class UserRequestDTO(BaseModel):
    name: str
    email:str