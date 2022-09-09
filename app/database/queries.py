from fastapi import HTTPException, status
from databases import Database
from sqlalchemy.sql import select
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from typing import List
from redis import Redis
import json

from .models import question, answer, category, question_category_associate, quiz, quiz_question_associate, quiz_result
from schemas.question import QuestionCreate, BaseQuestion, AnswerCreate, Answer, FullQuestion
from schemas.category import CategoryCreate, Category
from schemas.quiz import QuizCreate, QuizForAdmin, QuizUpdate, QuizQuestionsAdd, QuizQuestionAssociate, UserQuizResult


async def get_questions(db: Database, question_id: int = None):
    query = select([question, answer, category]).select_from(question) \
        .join(question_category_associate, isouter=True) \
        .join(category, isouter=True) \
        .join(answer).order_by(question.c.id)

    if question_id:
        query = query.where(question.c.id == question_id)

    return await db.fetch_all(query=query)


async def get_questions_categories(db: Database):
    join_1 = category.join(question_category_associate, category.c.id == question_category_associate.c.category_id) \
        .join(question, question.c.id == question_category_associate.c.question_id)
    query = select(question.c.id, category.c.id, category.c.name).select_from(join_1)

    return await db.fetch_all(query=query)


async def create_question(question_data: QuestionCreate, db: Database):
    transaction = await db.transaction().start()
    answers_data = question_data.pop('answers')

    query = question.insert().values(**question_data)

    try:
        new_question_id = await db.execute(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    for answer_data in answers_data:
        new_answer = await add_question_answer(answer_data, new_question_id, db)
        answer_data['question_id'] = new_answer.id

    question_data['id'] = new_question_id
    question_data['answers'] = answers_data

    await transaction.commit()

    return question_data


async def update_question(id: int, question_data: BaseQuestion, db: Database):
    query = question.update().values(**question_data).where(question.c.id == id) \
        .returning(question.c.id, question.c.question_text)

    try:
        query_result = await db.fetch_one(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    return query_result


async def delete_question(id: int, db: Database):
    query = question.delete().returning(question.c.id).where(question.c.id == id)
    return await db.fetch_one(query=query)


async def add_question_answer(answer_data: AnswerCreate, question_id: int, db: Database,
                              transaction: Database.transaction = None):
    query = answer.insert().values(**answer_data, question_id=question_id) \
        .returning(answer.c.id, answer.c.answer_text, answer.c.is_correct, answer.c.question_id)

    try:
        query_result = await db.fetch_one(query=query)
    except ForeignKeyViolationError as e:
        if transaction:
            await transaction.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    except UniqueViolationError as e:
        if transaction:
            await transaction.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    return Answer(**query_result)


async def update_question_answer(answer_id: int, question_data: BaseQuestion, question_id: int, db: Database):
    query = answer.update().where(answer.c.id == answer_id, answer.c.question_id == question_id) \
        .values(**question_data).returning(answer.c.id, answer.c.answer_text, answer.c.is_correct, answer.c.question_id)
    try:
        query_result = await db.fetch_one(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    return query_result


async def delete_question_answer(answer_id: int, question_id: int, db: Database):
    query = select([answer]).where(answer.c.question_id == question_id)
    all_answers = await db.fetch_all(query=query)

    if len(all_answers) == 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Question must have at least two answers")

    query = answer.delete().returning(answer.c.id).where(answer.c.id == answer_id, answer.c.question_id == question_id)
    return await db.fetch_one(query=query)


async def get_categories(db: Database):
    query = category.select()
    return await db.fetch_all(query=query)


async def create_category(category_data: CategoryCreate, db: Database):
    query = category.insert().values(**category_data).returning(category.c.id, category.c.name, category.c.description)

    try:
        query_result = await db.fetch_one(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    return query_result


async def update_category(category_id: int, category_data: CategoryCreate, db: Database):
    query = category.update().where(category.c.id == category_id).values(**category_data) \
        .returning(category.c.id, category.c.name, category.c.description)

    try:
        query_result = await db.fetch_one(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    return query_result


async def delete_category(category_id: int, db: Database):
    query = category.delete().returning(category.c.id).where(category.c.id == category_id)
    return await db.fetch_one(query=query)


async def add_question_category(category_id: int, question_id: int, db: Database):
    query = select([question_category_associate]) \
        .where(question_category_associate.c.category_id == category_id,
               question_category_associate.c.question_id == question_id)

    already_added = await db.fetch_all(query=query)

    if not already_added:
        query = question_category_associate.insert().values(category_id=category_id, question_id=question_id) \
            .returning(question_category_associate.c.id, question_category_associate.c.category_id,
                       question_category_associate.c.question_id)

        try:
            query_result = await db.fetch_one(query=query)
        except ForeignKeyViolationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=str(e))
        return query_result
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Question already has this category")


async def delete_question_category(category_id: int, question_id: int, db: Database):
    query = question_category_associate.delete().returning(question_category_associate.c.id) \
        .where(question_category_associate.c.category_id == category_id,
               question_category_associate.c.question_id == question_id)
    return await db.fetch_one(query=query)


async def get_quizzes(db: Database, quiz_id: int = None, active: bool = False):
    query = select([quiz])

    if quiz_id:
        query = query.where(quiz.c.id == quiz_id)
    if active:
        query = query.where(quiz.c.is_active == active)

    return await db.fetch_all(query=query)


async def get_quiz_questions(quiz_id: int, db: Database):
    sq = (select([quiz_question_associate]).where(quiz_question_associate.c.quiz_id == quiz_id)).alias('sq')

    query = select([question, answer, category]).select_from(question) \
        .join(sq) \
        .join(question_category_associate, isouter=True) \
        .join(category, isouter=True) \
        .join(answer).order_by(question.c.id)

    return await db.fetch_all(query=query)


async def get_quiz_questions_with_correct_answers(quiz_id: int, db: Database):
    sq_1 = (select([quiz_question_associate]).where(quiz_question_associate.c.quiz_id == quiz_id)).alias('sq_1')
    sq_2 = (select([answer]).where(answer.c.is_correct)).alias('sq_2')

    query = select([question.c.id, sq_2.c.id]).select_from(question) \
        .join(sq_1) \
        .join(sq_2) \
        .order_by(question.c.id)

    return await db.fetch_all(query=query)


async def create_quiz(quiz_data: QuestionCreate, db: Database):
    transaction = await db.transaction().start()

    questions = quiz_data.pop('questions')
    query = quiz.insert().values(**quiz_data).returning(quiz)

    try:
        new_quiz = await db.fetch_one(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    new_quiz_id = QuizForAdmin(**new_quiz).id

    await add_quiz_questions(new_quiz_id, questions, db, transaction)

    if len(questions) > 0:
        values_to_insert = [{'quiz_id': new_quiz_id, 'question_id': question_id} for question_id in questions]
        query = quiz_question_associate.insert().values(values_to_insert)
        await db.execute(query=query)

    await transaction.commit()

    return new_quiz


async def update_quiz(quiz_id: int, quiz_data: QuizUpdate, db: Database):
    query = quiz.update().values(**quiz_data).where(quiz.c.id == quiz_id).returning(quiz)
    try:
        query_result = await db.fetch_one(query=query)
    except UniqueViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    return query_result


async def delete_quiz(quiz_id: int, db: Database):
    query = quiz.delete().returning(quiz.c.id).where(quiz.c.id == quiz_id)
    return await db.fetch_one(query=query)


async def add_quiz_questions(quiz_id: int, questions_to_add: List[int], db: Database,
                             transaction: Database.transaction = None):
    query = select([quiz_question_associate]).where(quiz_question_associate.c.quiz_id == quiz_id)
    query_result = await db.fetch_all(query)
    already_added = [QuizQuestionAssociate(**item).question_id for item in query_result]
    intersection = set(questions_to_add).intersection(already_added)

    if len(intersection) > 0:
        if transaction:
            await transaction.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Questions with ids: {intersection} have already been added to the quiz")

    values_to_insert = [{'quiz_id': quiz_id, 'question_id': question_id} for question_id in questions_to_add]
    query = quiz_question_associate.insert().values(values_to_insert).returning(quiz_question_associate)

    try:
        query_result = await db.fetch_all(query=query)
    except ForeignKeyViolationError as e:
        if transaction:
            await transaction.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    return query_result


async def delete_quiz_question(quiz_id: int, question_id: int, db: Database):
    query = quiz_question_associate.delete().where(quiz_question_associate.c.quiz_id == quiz_id,
                                                   quiz_question_associate.c.question_id == question_id) \
        .returning(quiz_question_associate.c.id)
    return await db.fetch_one(query=query)


async def save_result_to_db(result_data: UserQuizResult, db: Database):
    result_data.pop('answers')
    query = quiz_result.insert().values(**result_data).returning(quiz_result)
    return await db.fetch_one(query=query)


async def get_quizzes_results(quiz_id, user, db: Database):
    query = select([quiz_result])

    if quiz_id:
        query = query.where(quiz_result.c.quiz_id == quiz_id)
    if user:
        query = query.where(quiz_result.c.user_email == user)

    return await db.fetch_all(query=query)


async def get_quiz_result(result_id: int, user: str, db: Database):
    query = select([quiz_result]).where(quiz_result.c.id == result_id)
    if user:
        query = query.where(quiz_result.c.user_email == user)

    return await db.fetch_all(query=query)


async def get_quiz_result_detail_from_cache(result_id, db: Redis):
    query = select([quiz_result]).where(quiz_result.c.id == result_id)
    return await db.fetch_all(query=query)


async def save_result_detail_to_cache(cache_key, data, cache: Redis):
    data['finished_at'] = str(data['finished_at'])
    await cache.set(cache_key, json.dumps(data))
    await cache.expire(cache_key, 172800)


async def get_result_detail_from_cache(key, cache: Redis):
    data = await cache.get(key)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Data for this quiz result does not exist or has been deleted')
    return data
