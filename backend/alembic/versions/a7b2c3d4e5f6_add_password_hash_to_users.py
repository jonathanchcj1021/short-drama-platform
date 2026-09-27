"""add password_hash to users

Revision ID: a7b2c3d4e5f6
Revises: 5e21c3f9a401
Create Date: 2026-09-28 00:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'a7b2c3d4e5f6'
down_revision: str | None = '5e21c3f9a401'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
