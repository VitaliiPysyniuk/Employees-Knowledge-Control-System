from fastapi import FastAPI
from databases import Database
from redis import Redis
from aioredis import from_url

from app.routers import users
from app.core.congif import settings
from app.database.injections import inject_dbs

db: Database = Database(settings.POSTGRES_DATABASE_URL)
cache: Redis = from_url(settings.REDIS_DATABASE_URL)

app = FastAPI()

app.include_router(users.router)


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


inject_dbs(app, db, cache)
