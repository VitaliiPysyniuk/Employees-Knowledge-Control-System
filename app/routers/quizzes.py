import os
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import FileResponse
from typing import List
from databases import Database
from redis import Redis
from copy import deepcopy
import json

from database.connection import get_db, get_cache
from database import queries
from schemas.question import QuestionWithAnswersForUser, QuestionWithAnswersForAdmin, QuestionWithCorrectAnswer
from schemas.quiz import *
from schemas.user import User
from utils import parse_questions, process_user_answers, form_user_cache_key, save_data_to_csv_file
from permissions import get_request_user, is_admin, is_user

user_router = APIRouter()
admin_router = APIRouter()


@user_router.get('', response_model=List[QuizForUser], dependencies=[Depends(is_user)])
@admin_router.get('', response_model=List[QuizForAdmin], dependencies=[Depends(is_admin)])
async def get_quizzes(db: Database = Depends(get_db), request_user: User = Depends(get_request_user)):
    if 'admin' not in request_user.roles:
        quizzes = await queries.get_quizzes(db, active=True)
    else:
        quizzes = await queries.get_quizzes(db)

    return quizzes


@admin_router.post('', response_model=QuizForAdmin, dependencies=[Depends(is_admin)])
async def create_quiz(data: QuizCreate, db: Database = Depends(get_db)):
    result = await queries.create_quiz(data.dict(), db)

    if result and 'error' in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=result['error'])

    return result


@user_router.get('/results', response_model=List[QuizResult], dependencies=[Depends(is_user)])
@admin_router.get('/results', response_model=List[QuizResult], dependencies=[Depends(is_admin)])
async def get_quizzes_results(quiz: int = None, user: str = None, db: Database = Depends(get_db),
                              request_user: User = Depends(get_request_user)):
    if 'admin' not in request_user.roles:
        user = request_user.email

    quizzes_results = await queries.get_quizzes_results(quiz, user, db)

    return quizzes_results


@user_router.get('/results/{result_id}', response_model=QuizResult, dependencies=[Depends(is_user)])
@admin_router.get('/results/{result_id}', response_model=QuizResult, dependencies=[Depends(is_admin)])
async def get_single_quiz_result(result_id: int, db: Database = Depends(get_db),
                                 request_user: User = Depends(get_request_user)):
    if 'admin' not in request_user.roles:
        quiz_result = await queries.get_quiz_result(result_id, request_user.email, db)
    else:
        quiz_result = await queries.get_quiz_result(result_id, None, db)

    if len(quiz_result) != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Quiz result with id: {result_id} was not found")

    return quiz_result[0]


@admin_router.get('/results/{result_id}/details', response_model=QuizResultDetailsForAdmin,
                  dependencies=[Depends(is_admin)])
async def get_quiz_result_details(result_id: int, csv_mode: bool = False, db: Database = Depends(get_db),
                                  cache: Redis = Depends(get_cache)):
    quiz_result = await queries.get_quiz_result(result_id, None, db)

    if len(quiz_result) != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Quiz result with id: {result_id} was not found")
    quiz_result = QuizResult(**quiz_result[0])

    key = form_user_cache_key(quiz_result.user_email, quiz_result.quiz_id, quiz_result.finished_at)
    quiz_result_details = await queries.get_result_detail_from_cache(key, cache)

    if csv_mode:
        filename = save_data_to_csv_file(quiz_result_details)
        file_path = f'csv-files/{filename}'
        if os.path.exists(file_path):
            return FileResponse(file_path)

    return json.loads(quiz_result_details)


@user_router.get('/{quiz_id}', response_model=QuizForUser, dependencies=[Depends(is_user)])
@admin_router.get('/{quiz_id}', response_model=QuizForAdmin, dependencies=[Depends(is_admin)])
async def get_single_quiz(quiz_id: int, db: Database = Depends(get_db)):
    quizzes = await queries.get_quizzes(db, quiz_id)

    if len(quizzes) != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Quiz with id: {quiz_id} was not found")

    return quizzes[0]


@admin_router.patch('/{quiz_id}', response_model=QuizForAdmin, dependencies=[Depends(is_admin)])
async def update_quiz(quiz_id: int, data: QuizUpdate, db: Database = Depends(get_db)):
    result = await queries.update_quiz(quiz_id, data.dict(), db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Quiz with id: {quiz_id} was not found")

    return result


@admin_router.delete('/{quiz_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_admin)])
async def delete_quiz(quiz_id: int, db: Database = Depends(get_db)):
    result = await queries.delete_quiz(quiz_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Quiz with id: {quiz_id} was not found")


@user_router.get('/{quiz_id}/questions', response_model=List[QuestionWithAnswersForUser],
                 dependencies=[Depends(is_user)])
@admin_router.get('/{quiz_id}/questions', response_model=List[QuestionWithAnswersForAdmin],
                  dependencies=[Depends(is_admin)])
async def get_quiz_questions(quiz_id: int, db: Database = Depends(get_db)):
    quiz_questions = await queries.get_quiz_questions(quiz_id, db)
    quiz_questions = parse_questions(quiz_questions)

    return quiz_questions


@admin_router.post('/{quiz_id}/questions', response_model=List[QuizQuestionAssociate], dependencies=[Depends(is_admin)])
async def add_quiz_questions(quiz_id: int, data: QuizQuestionsAdd, db: Database = Depends(get_db)):
    result = await queries.add_quiz_questions(quiz_id, data.questions, db)
    print(result)
    return result


@admin_router.delete('/{quiz_id}/questions/{question_id}', status_code=status.HTTP_204_NO_CONTENT,
                     dependencies=[Depends(is_admin)])
async def delete_quiz_question(quiz_id: int, question_id: int, db: Database = Depends(get_db)):
    result = await queries.delete_quiz_question(quiz_id, question_id, db)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Quiz doesn't include question with id: {question_id}")


@user_router.post('/{quiz_id}/user-answers', response_model=UserQuizResult, dependencies=[Depends(is_user)])
async def process_user_result(quiz_id: int, data: UserAnswers, db: Database = Depends(get_db),
                              cache: Redis = Depends(get_cache), request_user: User = Depends(get_request_user)):
    quiz_questions = await queries.get_quiz_questions_with_correct_answers(quiz_id, db)
    quiz_questions = [QuestionWithCorrectAnswer(**question).dict() for question in quiz_questions]

    user_quiz_result = process_user_answers(quiz_questions, data.dict()['answers'])
    user_quiz_result['quiz_id'] = quiz_id
    user_quiz_result['user_email'] = request_user.email

    key = form_user_cache_key(request_user.email, quiz_id, user_quiz_result['finished_at'])
    await queries.save_result_detail_to_cache(key, deepcopy(user_quiz_result), cache)
    result = await queries.save_result_to_db(user_quiz_result, db)

    return result
