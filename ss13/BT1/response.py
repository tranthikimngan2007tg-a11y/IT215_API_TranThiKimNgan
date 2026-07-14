from pydantic import BaseModel
from typing import Optional, Any


class APIResponse(BaseModel):
    statusCode: int
    message: str
    error: Optional[Any] = None
    data: Optional[Any] = None
    path: str
    timestamp: str

