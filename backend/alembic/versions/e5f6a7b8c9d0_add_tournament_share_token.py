"""add tournament share_token

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-17 14:00:00.000000

"""
import secrets
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('share_token', sa.String(), nullable=True))

    # Backfill existing rows with a unique token so they stay shareable.
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id FROM tournaments")).fetchall()
    for (tid,) in rows:
        bind.execute(
            sa.text("UPDATE tournaments SET share_token = :tok WHERE id = :id"),
            {"tok": secrets.token_urlsafe(12), "id": tid},
        )

    op.create_index(
        op.f('ix_tournaments_share_token'),
        'tournaments',
        ['share_token'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tournaments_share_token'), table_name='tournaments')
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.drop_column('share_token')
