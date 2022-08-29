from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Float, ForeignKey, Table, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

user = Table(
    'users',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('email', String(50), unique=True, nullable=False),
    Column('name', String(50), nullable=False),
    Column('is_superuser', Boolean, server_default=text("false")),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now()),
    Column('password_id', Integer, ForeignKey('passwords.id'), unique=True, nullable=False)
)

password = Table(
    'passwords',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('password', String(32), nullable=False)
)

quiz_result = Table(
    'quiz_results',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_score', Float, server_default=text("0.0")),
    Column('max_score', Float, server_default=text("0.0")),
    Column('finished_at', DateTime, server_default=func.now()),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'))
)

quiz = Table(
    'quizzes',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('title', Integer, nullable=False),
    Column('description', String(200), nullable=False),
    Column('is_active', Boolean, server_default=text("true"))
)

question_category_associate = Table(
    'questions_categories',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='SET NULL'))
)

question = Table(
    'questions',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('question_text', String(200), nullable=False),
    Column('quiz_id', Integer, ForeignKey('quizzes.id', ondelete='SET NULL'))
)

category = Table(
    'categories',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), nullable=False),
    Column('description', String(200), nullable=False)
)

answer = Table(
    'answers',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('answer_text', String(200), nullable=False),
    Column('is_correct', Boolean, nullable=False),
    Column('question_id', Integer, ForeignKey('questions.id', ondelete='CASCADE'))
)
