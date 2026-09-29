"""add source to dramas

Revision ID: d1e2f3a4b5c6
Revises: a7b2c3d4e5f6
Create Date: 2026-09-29 11:05:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3a4b5c6'
down_revision: str | None = 'a7b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 已有劇集全部來自紅果短劇，用 server_default 一次性回填舊列
    op.add_column(
        'dramas',
        sa.Column(
            'source',
            sa.String(length=32),
            nullable=False,
            server_default='hongguo',
        ),
    )


def downgrade() -> None:
    op.drop_column('dramas', 'source')
