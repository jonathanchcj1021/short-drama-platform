"""add hongguo_series_id to dramas

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-09-29 11:20:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'e2f3a4b5c6d7'
down_revision: str | None = 'd1e2f3a4b5c6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'dramas',
        sa.Column('hongguo_series_id', sa.String(length=64), nullable=True),
    )
    op.create_index(
        'ix_dramas_hongguo_series_id', 'dramas', ['hongguo_series_id']
    )


def downgrade() -> None:
    op.drop_index('ix_dramas_hongguo_series_id', table_name='dramas')
    op.drop_column('dramas', 'hongguo_series_id')
