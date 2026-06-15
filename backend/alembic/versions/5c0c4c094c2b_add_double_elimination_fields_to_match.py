"""add double elimination fields to match

Revision ID: 5c0c4c094c2b
Revises: ec06d6397560
Create Date: 2026-06-15 10:18:42.483620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c0c4c094c2b'
down_revision: Union[str, Sequence[str], None] = 'ec06d6397560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Batch mode so SQLite can add the self-referential foreign key.
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bracket', sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column('loser_next_match_id', sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                'loser_next_match_slot',
                sa.Enum('A', 'B', name='matchslot'),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            'fk_matches_loser_next_match_id',
            'matches',
            ['loser_next_match_id'],
            ['id'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_matches_loser_next_match_id', type_='foreignkey'
        )
        batch_op.drop_column('loser_next_match_slot')
        batch_op.drop_column('loser_next_match_id')
        batch_op.drop_column('bracket')
