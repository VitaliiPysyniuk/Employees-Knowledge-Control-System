from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from utils import Auth0
from schemas.user import User

token_auth_scheme = HTTPBearer()


def get_request_user(token: str = Depends(token_auth_scheme)) -> User:
    token_payload = Auth0.verify(token.credentials)

    return User(email=token_payload['email'], name=token_payload['name'], auth0_id=token_payload['sub'],
                roles=token_payload['role'])


def is_authenticated(token: str = Depends(token_auth_scheme)):
    Auth0.verify(token.credentials)


def is_user(request_user: User = Depends(get_request_user)):
    if 'user' not in request_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You don\'t have permissions to access / on this server')


def is_admin(request_user: User = Depends(get_request_user)):
    if 'admin' not in request_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You don\'t have permissions to access / on this server')
