from pydantic import BaseModel
from typing import Optional, List


class AnswerCreate(BaseModel):
    answer_text: str
    is_correct: Optional[bool] = False


class BaseAnswer(BaseModel):
    answer_text: str
    is_correct: bool
    question_id: int


class Answer(BaseAnswer):
    id: int


class BaseQuestion(BaseModel):
    question_text: str


class Category(BaseModel):
    id: int
    name: str


class Question(BaseQuestion):
    id: int


class AnswerInQuestionsListForUser(BaseModel):
    id: int
    answer_text: str


class AnswerInQuestionsListForAdmin(BaseModel):
    id: int
    answer_text: str
    is_correct: bool


class QuestionWithAnswersForUser(Question):
    answers: List[AnswerInQuestionsListForUser]
    categories: List[Category]


class QuestionWithAnswersForAdmin(Question):
    answers: List[AnswerInQuestionsListForAdmin]
    categories: List[Category]


class QuestionWithAnswer(BaseModel):
    id: int
    question_text: str
    id_1: Optional[int]
    answer_text: Optional[str]
    is_correct: Optional[bool]
    question_id: Optional[int]


class QuestionCreate(BaseModel):
    question_text: str
    answers: Optional[List[AnswerCreate]] = []


class QuestionCategory(BaseModel):
    id: int
    name: str
    id_1: int


class FullQuestion(BaseModel):
    id: int
    question_text: Optional[str]
    id_1: Optional[int]
    answer_text: Optional[str]
    is_correct: Optional[bool] = False
    id_2: Optional[int]
    name: Optional[str]
    description: Optional[str]


class QuestionWithCorrectAnswer(BaseModel):
    id: int
    id_1: int
