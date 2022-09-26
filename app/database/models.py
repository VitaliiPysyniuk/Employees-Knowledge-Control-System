from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Float, ForeignKey, Table, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

quiz = Table(
    'quizzes',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(100), nullable=False, unique=True),
    Column('description', String(200), nullable=False),
    Column('is_active', Boolean, server_default=text("true"))
)

quiz_result = Table(
    'quiz_results',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_score', Float, server_default=text("0.0")),
    Column('max_score', Float, server_default=text("0.0")),
    Column('finished_at', DateTime, server_default=func.now()),
    Column('user_email', String(50), nullable=False),
    Column('quiz_id', Integer, ForeignKey('quizzes.id', ondelete='SET NULL')),
)

question_category_associate = Table(
    'questions_categories',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('question_id', Integer, ForeignKey('questions.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

question = Table(
    'questions',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('question_text', String(200), nullable=False, unique=True)
)

quiz_question_associate = Table(
    'quizzes_questions',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('quiz_id', Integer, ForeignKey('quizzes.id', ondelete='CASCADE')),
    Column('question_id', Integer, ForeignKey('questions.id', ondelete='CASCADE'))
)

category = Table(
    'categories',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), nullable=False, unique=True),
    Column('description', String(200), nullable=False)
)

answer = Table(
    'answers',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('answer_text', String(200), nullable=False, unique=True),
    Column('is_correct', Boolean, nullable=False),
    Column('question_id', Integer, ForeignKey('questions.id', ondelete='CASCADE'))
)
