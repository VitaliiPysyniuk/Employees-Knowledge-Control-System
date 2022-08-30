from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class UserSignUp(UserSignIn):
    name: str


class User(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
