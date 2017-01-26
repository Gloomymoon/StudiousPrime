"""initial migration

Revision ID: 9cb2a9e67e80
Revises: None
Create Date: 2017-01-22 16:46:53.105000

"""

# revision identifiers, used by Alembic.
revision = '9cb2a9e67e80'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('english_recognition',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('english_question', sa.Boolean(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('current', sa.Integer(), nullable=True),
    sa.Column('passed', sa.Integer(), nullable=True),
    sa.Column('create_dt', sa.DateTime(), nullable=True),
    sa.Column('finish_dt', sa.DateTime(), nullable=True),
    sa.Column('timeout', sa.Integer(), nullable=True),
    sa.Column('use_image', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.drop_table('english_myerrors')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('english_myerrors',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('word_id', sa.INTEGER(), nullable=False),
    sa.Column('exercise_id', sa.INTEGER(), nullable=False),
    sa.Column('answer', sa.TEXT(length=64), nullable=True),
    sa.Column('question', sa.TEXT(length=200), nullable=True),
    sa.ForeignKeyConstraint(['exercise_id'], [u'english_myexercises.id'], ),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], ),
    sa.ForeignKeyConstraint(['word_id'], [u'english_words.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'word_id', 'exercise_id')
    )
    op.drop_table('english_recognition')
    ### end Alembic commands ###