from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    email : str
    age: int
    password: str

class UserCreate(User):
    pass

class UserResponse(User):
    id: int
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None