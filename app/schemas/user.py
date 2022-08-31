from pydantic import BaseModel, EmailStr


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class UserSignInSuccess(BaseModel):
    access_token: str
    refresh_token: str


class UserSignUp(UserSignIn):
    name: str


class UserSignUpSuccess(BaseModel):
    email: EmailStr
    name: str
    email_verified: bool


class User(BaseModel):
    email: EmailStr
    name: str
    auth0_id: str
