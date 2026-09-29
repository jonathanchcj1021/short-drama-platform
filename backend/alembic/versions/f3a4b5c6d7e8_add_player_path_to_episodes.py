"""add player_path to episodes

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-09-29 11:30:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a4b5c6d7e8'
down_revision: str | None = 'e2f3a4b5c6d7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'episodes',
        sa.Column('player_path', sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('episodes', 'player_path')
