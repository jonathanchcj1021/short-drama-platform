"""add is_admin to users

Revision ID: 5e21c3f9a401
Revises: c608da26c891
Create Date: 2026-09-27 23:20:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '5e21c3f9a401'
down_revision: str | None = 'c608da26c891'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
