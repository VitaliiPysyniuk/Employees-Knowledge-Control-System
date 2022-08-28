from fastapi import APIRouter, Depends, Request
from databases import Database

from app.database.connection import get_db

router = APIRouter()


@router.get("/")
async def login(db: Database = Depends(get_db)):
    return {"status": "Working"}
