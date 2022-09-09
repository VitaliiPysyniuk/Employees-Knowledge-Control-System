from fastapi import FastAPI
from databases import Database
from redis import Redis
from aioredis import from_url
from aiohttp import ClientSession

from routers import users, questions, categories, quizzes
from core.congif import settings
from database.injections import inject_dbs

db: Database = Database(settings.POSTGRES_DATABASE_URL)
cache: Redis = from_url(settings.REDIS_DATABASE_URL)
# session: ClientSession = ClientSession()

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.connect()
    inject_dbs(app, db, cache)
    # app.state.session = session


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
    # await session.close()


app.include_router(users.router, prefix='/users', tags=['users'])
app.include_router(quizzes.user_router, prefix='/quizzes', tags=['quizzes'])
app.include_router(quizzes.admin_router, prefix='/admin/quizzes', tags=['quizzes-for-admin'])
app.include_router(questions.router, prefix='/admin/questions', tags=['questions-for-admin'])
app.include_router(categories.router, prefix='/admin/categories', tags=['categories-for-admin'])

