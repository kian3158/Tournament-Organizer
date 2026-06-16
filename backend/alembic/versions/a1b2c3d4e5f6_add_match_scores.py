"""add match scores

Revision ID: a1b2c3d4e5f6
Revises: 5c0c4c094c2b
Create Date: 2026-06-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '5c0c4c094c2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('score_a', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('score_b', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.drop_column('score_b')
        batch_op.drop_column('score_a')
