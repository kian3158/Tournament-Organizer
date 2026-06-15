"""add participant tournament_id seed and tournament format

Revision ID: dd5bfce28ced
Revises: ab6c4f4e8fde
Create Date: 2026-06-15 09:12:53.160360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd5bfce28ced'
down_revision: Union[str, Sequence[str], None] = 'ab6c4f4e8fde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tournament_format = sa.Enum(
    'SINGLE_ELIM', 'DOUBLE_ELIM', 'ROUND_ROBIN', 'SWISS', name='tournamentformat'
)


def upgrade() -> None:
    """Upgrade schema."""
    # Batch mode so SQLite (which can't ALTER to add FKs) recreates the table;
    # works unchanged on PostgreSQL too.
    with op.batch_alter_table('participants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tournament_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('seed', sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_participants_tournament_id'),
            ['tournament_id'],
            unique=False,
        )
        batch_op.create_foreign_key(
            'fk_participants_tournament_id',
            'tournaments',
            ['tournament_id'],
            ['id'],
        )

    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('format', tournament_format, nullable=False)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.drop_column('format')

    with op.batch_alter_table('participants', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_participants_tournament_id', type_='foreignkey'
        )
        batch_op.drop_index(batch_op.f('ix_participants_tournament_id'))
        batch_op.drop_column('seed')
        batch_op.drop_column('tournament_id')
