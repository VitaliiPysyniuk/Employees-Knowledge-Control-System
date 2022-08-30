from fastapi import FastAPI
from databases import Database
from redis import Redis
from aioredis import from_url

from routers import users
from core.congif import settings
from database.injections import inject_dbs

db: Database = Database(settings.POSTGRES_DATABASE_URL)
cache: Redis = from_url(settings.REDIS_DATABASE_URL)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.connect()
    inject_dbs(app, db, cache)


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


app.include_router(users.router, prefix='/users', tags=['users'])

