import os
from pydantic import BaseSettings, RedisDsn, PostgresDsn
from dotenv import load_dotenv

load_dotenv('../.env')


class Settings(BaseSettings):
    # [DATABASE]
    PG_USER: str = os.environ.get('POSTGRES_USER')
    PG_PASSWORD: str = os.environ.get('POSTGRES_PASSWORD')
    PG_HOST: str = os.environ.get('POSTGRES_HOST')
    PG_PORT: str = os.environ.get('POSTGRES_PORT')
    PG_DB: str = os.environ.get('POSTGRES_DB')

    POSTGRES_DATABASE_URL: PostgresDsn = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'

    # [CACHE]
    REDIS_PASSWORD: str = os.environ.get('REDIS_PASSWORD')
    REDIS_HOST: str = os.environ.get('REDIS_HOST')
    REDIS_PORT: str = os.environ.get('REDIS_PORT')
    REDIS_DB: str = os.environ.get('REDIS_DB')

    REDIS_DATABASE_URL: RedisDsn = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    # [AUTH0]
    DOMAIN: str = os.environ.get('DOMAIN')
    AUDIENCE: str = os.environ.get('AUDIENCE')
    ISSUER: str = os.environ.get('ISSUER')
    ALGORITHMS: str = os.environ.get('ALGORITHMS')
    CLIENT_ID: str = os.environ.get('CLIENT_ID')
    CLIENT_SECRET: str = os.environ.get('CLIENT_SECRET')
    CONNECTION: str = os.environ.get('CONNECTION')

    class Config:
        case_sensitive = True


settings = Settings()
