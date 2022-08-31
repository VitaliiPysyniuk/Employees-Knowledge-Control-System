from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from aiohttp import ClientSession
from six.moves.urllib.request import urlopen
import json
from jose import jwt

from core.congif import settings
from schemas.user import User, UserSignIn, UserSignUp

token_auth_scheme = HTTPBearer()


def get_session(request: Request) -> ClientSession:
    return request.app.state.session


def get_request_user(token: str = Depends(token_auth_scheme)) -> User:
    token_payload = Auth0.verify(token.credentials)

    return User(email=token_payload['email'], name=token_payload['name'], auth0_id=token_payload['sub'])


class Auth0:
    @classmethod
    async def login(cls, user_creds: UserSignIn, session: ClientSession):
        payload = {
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'audience': settings.AUDIENCE,
            'username': user_creds.email,
            'password': user_creds.password,
            'grant_type': 'password',
            'scope': 'openid offline_access'
        }
        url = f'https://{settings.DOMAIN}/oauth/token'

        async with session.post(url, json=payload) as response:
            result = await response.json()
            status_code = response.status

        return result, status_code

    @classmethod
    def verify(cls, token):
        jsonurl = urlopen("https://" + settings.DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=settings.ALGORITHMS,
                    audience=settings.AUDIENCE,
                    issuer="https://" + settings.DOMAIN + "/"
                )
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token is expired')
            except jwt.JWTClaimsError:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail='Incorrect claims, please check the audience and issuer')
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unable to parse access token')

        return payload

    @classmethod
    async def register(cls, new_user_data: UserSignUp, session: ClientSession):
        payload = {
            'client_id': settings.CLIENT_ID,
            'connection': settings.CONNECTION,
            'email': new_user_data.email,
            'password': new_user_data.password,
            'name': new_user_data.name,
        }
        url = f'https://{settings.DOMAIN}/dbconnections/signup'

        async with session.post(url, json=payload) as response:
            result = await response.json()
            status_code = response.status

        return result, status_code

