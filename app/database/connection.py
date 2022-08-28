from fastapi import Request
from databases import Database
from redis import Redis


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_cache(request: Request) -> Redis:
    return request.app.state.cache
