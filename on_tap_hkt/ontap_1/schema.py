from pydantic import BaseModel

class BookRequestlDTO(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    status: str