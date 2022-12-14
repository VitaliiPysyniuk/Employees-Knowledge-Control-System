from pydantic import BaseModel, EmailStr
from typing import List


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
    roles: List[str]


class Auth0UserRegister(UserSignUp):
    client_id: str
    connection: str


class Auth0UserLogin(BaseModel):
    client_id: str
    client_secret: str
    audience: str
    username: EmailStr
    password: str
    grant_type: str
    scope: str
