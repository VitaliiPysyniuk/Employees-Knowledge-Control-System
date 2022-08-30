from fastapi import APIRouter, Depends
from databases import Database

from database.connection import get_db

router = APIRouter()


@router.get("/")
async def login(db: Database = Depends(get_db)):
    return {"status": "Working"}
