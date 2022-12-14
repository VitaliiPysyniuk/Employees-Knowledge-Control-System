"""empty message

Revision ID: dbe4b4161476
Revises: 1b29a7e5159f
Create Date: 2022-09-06 21:20:00.254181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbe4b4161476'
down_revision = '1b29a7e5159f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('quizzes', 'title',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=100),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('quizzes', 'title',
               existing_type=sa.String(length=100),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
