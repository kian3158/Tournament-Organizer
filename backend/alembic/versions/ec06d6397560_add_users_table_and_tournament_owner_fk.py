"""add users table and tournament owner fk

Revision ID: ec06d6397560
Revises: dd5bfce28ced
Create Date: 2026-06-15 09:37:53.756934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec06d6397560'
down_revision: Union[str, Sequence[str], None] = 'dd5bfce28ced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Batch mode so SQLite can add the foreign key (plain ALTER ADD FK fails).
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_tournaments_owner_id'), ['owner_id'], unique=False
        )
        batch_op.create_foreign_key(
            'fk_tournaments_owner_id', 'users', ['owner_id'], ['id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tournaments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_tournaments_owner_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_tournaments_owner_id'))

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
