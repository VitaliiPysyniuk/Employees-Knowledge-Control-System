from fastapi import APIRouter, Depends, Response, status, HTTPException
from typing import List
from databases import Database

from database.connection import get_db
from database import queries
from schemas.user import User, UserSignUp


router = APIRouter()


@router.get('/', response_model=List[User])
async def get_users(db: Database = Depends(get_db)):
    users = await queries.get_users(db)
    return users


@router.post('/', response_model=User)
async def get_users(data: UserSignUp, db: Database = Depends(get_db)):
    data = data.dict()
    new_user_id = await queries.create_user(data, db)
    new_user = await queries.get_user_by_id(new_user_id, db)

    return new_user


@router.delete('/{id}')
async def delete_user(id: int, db: Database = Depends(get_db)):
    user_before_delete = await queries.get_user_by_id(id, db)

    if not user_before_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")

    await queries.delete_user(id, db)
    user_after_delete = await queries.get_user_by_id(id, db)

    if not user_after_delete:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
