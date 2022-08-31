from fastapi import FastAPI
from databases import Database
from redis import Redis
from aioredis import from_url
from aiohttp import ClientSession

from routers import users, root
from core.congif import settings
from database.injections import inject_dbs

db: Database = Database(settings.POSTGRES_DATABASE_URL)
cache: Redis = from_url(settings.REDIS_DATABASE_URL)
session: ClientSession = ClientSession()

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.connect()
    inject_dbs(app, db, cache)
    app.state.session = session


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    await session.close()


app.include_router(root.router)
app.include_router(users.router, prefix='/users', tags=['users'])

