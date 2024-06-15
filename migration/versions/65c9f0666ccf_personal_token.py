"""personal token

Revision ID: 65c9f0666ccf
Revises: 174f919a0ab1
Create Date: 2024-06-15 13:58:23.373003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65c9f0666ccf'
down_revision: Union[str, None] = '174f919a0ab1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tokens', sa.Column('tg_login', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tokens', 'tg_login')
    # ### end Alembic commands ###