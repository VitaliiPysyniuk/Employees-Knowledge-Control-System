from fastapi import APIRouter, Depends, HTTPException
from aiohttp import ClientSession


from schemas.user import UserSignIn, UserSignInSuccess, User, UserSignUp, UserSignUpSuccess
from utils import get_session, Auth0, get_request_user

router = APIRouter()


@router.post('/login', response_model=UserSignInSuccess)
async def login(user_creds: UserSignIn, session: ClientSession = Depends(get_session)):
    data, status_code = await Auth0.login(user_creds, session)

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data)

    return data


@router.post('/register', status_code=201, response_model=UserSignUpSuccess)
async def register(new_user_data: UserSignUp, session: ClientSession = Depends(get_session)):
    data, status_code = await Auth0.register(new_user_data, session)

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data['description'])

    return data


@router.get('/protected_example')
async def private(request_user: User = Depends(get_request_user)):

    return request_user
