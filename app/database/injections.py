from fastapi import FastAPI
from databases import Database
from redis import Redis
from starlette.routing import Mount


def inject_dbs(app: FastAPI, db: Database, cache: Redis):
    app.state.db = db
    app.state.cache = cache
    for route in app.router.routes:
        if isinstance(route, Mount):
            route.app.state.db = db
            route.app.state.cache = cache
