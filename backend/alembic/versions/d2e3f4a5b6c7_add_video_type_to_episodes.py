"""add video_type to episodes

Revision ID: d2e3f4a5b6c7
Revises: c7d8e9f0a1b2
Create Date: 2026-09-29 16:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'd2e3f4a5b6c7'
down_revision: str | None = 'c7d8e9f0a1b2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'episodes',
        sa.Column('video_type', sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('episodes', 'video_type')
