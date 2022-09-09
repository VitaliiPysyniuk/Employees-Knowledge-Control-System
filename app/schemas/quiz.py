from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class QuizCreate(BaseModel):
    title: str
    description: str
    is_active: Optional[bool] = True
    questions: Optional[List[int]] = []


class QuizQuestionsAdd(BaseModel):
    questions: List[int]


class QuizUpdate(BaseModel):
    title: str
    description: str
    is_active: bool


class QuizForUser(BaseModel):
    id: int
    title: str
    description: str


class QuizForAdmin(BaseModel):
    id: int
    title: str
    description: str
    is_active: bool

# toooooooooooooooooooooooooooooo deleteeeeeeeeeeeeeeeeeeeeeeee
# toooooooooooooooooooooooooooooo deleteeeeeeeeeeeeeeeeeeeeeeee
# toooooooooooooooooooooooooooooo deleteeeeeeeeeeeeeeeeeeeeeeee
# toooooooooooooooooooooooooooooo deleteeeeeeeeeeeeeeeeeeeeeeee
# class Quiz(BaseModel):
#     id: int
#     title: str
#     description: str
#     is_active: bool


class QuizQuestionAssociate(BaseModel):
    id: int
    quiz_id: int
    question_id: int


class UserAnswer(BaseModel):
    question_id: int
    answer_id: int


class UserAnswers(BaseModel):
    answers: List[UserAnswer]


class UserQuizResult(BaseModel):
    quiz_id: int
    user_score: int
    max_score: int
    finished_at: datetime
    user_email: EmailStr


class QuizResult(UserQuizResult):
    id: int


class QuizResultAnswer(BaseModel):
    question_id: int
    user_answer_id: int
    correct_answer_id: int
    is_correct: bool


class QuizResultAnswerForUser(BaseModel):
    question_id: int
    user_answer_id: int
    correct_answer_id: int
    is_correct: bool


class QuizResultDetailsForAdmin(UserQuizResult):
    answers: List[QuizResultAnswer]


class QuizResultDetailsForUser(UserQuizResult):
    answers: List[QuizResultAnswerForUser]
