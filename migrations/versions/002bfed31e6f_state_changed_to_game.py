"""state changed to game

Revision ID: 002bfed31e6f
Revises: 
Create Date: 2021-03-15 21:21:57.518112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002bfed31e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('games', 'state', new_column_name='game')


def downgrade():
    op.alter_column('games', 'game', new_column_name='state')
