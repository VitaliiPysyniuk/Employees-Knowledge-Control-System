from fastapi import APIRouter, status, HTTPException, Depends
from databases import Database
from typing import List

from database import queries
from database.connection import get_db
from schemas.category import CategoryCreate, Category
from permissions import is_admin

router = APIRouter()


@router.get('', response_model=List[Category], dependencies=[Depends(is_admin)])
async def get_categories(db: Database = Depends(get_db)):
    categories = await queries.get_categories(db)
    return categories


@router.post('', response_model=Category, dependencies=[Depends(is_admin)])
async def create_category(data: CategoryCreate, db: Database = Depends(get_db)):
    result = await queries.create_category(data.dict(), db)
    return result


@router.patch('/{category_id}', response_model=Category, dependencies=[Depends(is_admin)])
async def update_category(category_id: int, data: CategoryCreate, db: Database = Depends(get_db)):
    result = await queries.update_category(category_id, data.dict(), db)
    return result


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_admin)])
async def delete_category(category_id: int, db: Database = Depends(get_db)):
    result = await queries.delete_category(category_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Category with id: {category_id} was not found")
