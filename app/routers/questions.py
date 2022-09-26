from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from databases import Database

from database.connection import get_db
from database import queries
from schemas.question import Question, QuestionWithAnswersForAdmin, QuestionCreate, BaseQuestion, AnswerCreate, Answer
from utils import parse_questions
from permissions import is_admin

router = APIRouter()


@router.get('', response_model=List[QuestionWithAnswersForAdmin], dependencies=[Depends(is_admin)])
async def get_questions(db: Database = Depends(get_db)):
    questions = await queries.get_questions(db)
    questions = parse_questions(questions)

    return questions


@router.post('', response_model=QuestionWithAnswersForAdmin, dependencies=[Depends(is_admin)])
async def create_question(data: QuestionCreate, db: Database = Depends(get_db)):
    if len(data.answers) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Question must have at least two answers")

    result = await queries.create_question(data.dict(), db)
    return result


@router.get('/{id}', response_model=QuestionWithAnswersForAdmin, dependencies=[Depends(is_admin)])
async def get_single_question(id: int, db: Database = Depends(get_db)):
    questions = await queries.get_questions(db, id)
    questions = parse_questions(questions)

    if len(questions) != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question with id: {id} was not found")


    return questions[0]


@router.patch('/{id}', response_model=Question, dependencies=[Depends(is_admin)])
async def update_question(id: int, data: BaseQuestion, db: Database = Depends(get_db)):
    result = await queries.update_question(id, data.dict(), db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question with id: {id} was not found")

    return result


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_admin)])
async def delete_question(id: int, db: Database = Depends(get_db)):
    result = await queries.delete_question(id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question with id: {id} was not found")


@router.post('/{question_id}/answers', response_model=Answer, dependencies=[Depends(is_admin)])
async def create_question_answer(question_id: int, data: AnswerCreate, db: Database = Depends(get_db)):
    result = await queries.add_question_answer(data.dict(), question_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question with id: {question_id} was not found")

    return result


@router.patch('/{question_id}/answers/{answer_id}', response_model=Answer, dependencies=[Depends(is_admin)])
async def update_question_answer(question_id: int, answer_id: int, data: AnswerCreate,
                                 db: Database = Depends(get_db)):
    result = await queries.update_question_answer(answer_id, data.dict(), question_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question or answer with such ids doesn't exist")

    return result


@router.delete('/{question_id}/answers/{answer_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(is_admin)])
async def delete_question_answer(question_id: int, answer_id: int, db: Database = Depends(get_db)):
    result = await queries.delete_question_answer(answer_id, question_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Answer with id: {answer_id} was not found")


@router.post('/{question_id}/categories/{category_id}', status_code=status.HTTP_200_OK,
             dependencies=[Depends(is_admin)])
async def add_question_category(question_id: int, category_id: int, db: Database = Depends(get_db)):
    result = await queries.add_question_category(category_id, question_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question or category with such ids doesn't exist")

    return result


@router.delete('/{question_id}/categories/{category_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(is_admin)])
async def delete_question_category(question_id: int, category_id: int, db: Database = Depends(get_db)):
    result = await queries.delete_question_category(category_id, question_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Question or category with such ids doesn't exist")
