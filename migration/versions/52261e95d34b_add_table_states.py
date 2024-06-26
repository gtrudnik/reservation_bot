"""add table states

Revision ID: 52261e95d34b
Revises: a93e62bb1ac2
Create Date: 2024-05-29 15:24:37.331259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52261e95d34b'
down_revision: Union[str, None] = 'a93e62bb1ac2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('states',
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.chat_id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_unique_constraint(None, 'tokens', ['token'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tokens', type_='unique')
    op.drop_table('states')
    # ### end Alembic commands ###
