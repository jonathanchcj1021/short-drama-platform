"""add membership tier, vip expiry, paid dramas, episode unlocks

Revision ID: b1c2d3e4f5a6
Revises: f3a4b5c6d7e8
Create Date: 2026-09-29 12:00:00.000000
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5a6'
down_revision: str | None = 'f3a4b5c6d7e8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # users：會員等級 + VIP 到期日
    op.add_column(
        'users',
        sa.Column(
            'membership_tier',
            sa.String(length=20),
            nullable=False,
            server_default='free',
        ),
    )
    op.add_column(
        'users',
        sa.Column('vip_expires_at', sa.DateTime(timezone=True), nullable=True),
    )

    # dramas：預設全部劇都係收費劇
    op.add_column(
        'dramas',
        sa.Column(
            'is_paid',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    # episode_unlocks：免費用戶睇過廣告之後解鎖咗嘅集
    op.create_table(
        'episode_unlocks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'user_id',
            sa.Integer(),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'episode_id',
            sa.Integer(),
            sa.ForeignKey('episodes.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint('user_id', 'episode_id', name='uq_episode_unlocks_user_episode'),
    )
    op.create_index('ix_episode_unlocks_user_id', 'episode_unlocks', ['user_id'])
    op.create_index('ix_episode_unlocks_episode_id', 'episode_unlocks', ['episode_id'])


def downgrade() -> None:
    op.drop_index('ix_episode_unlocks_episode_id', table_name='episode_unlocks')
    op.drop_index('ix_episode_unlocks_user_id', table_name='episode_unlocks')
    op.drop_table('episode_unlocks')
    op.drop_column('dramas', 'is_paid')
    op.drop_column('users', 'vip_expires_at')
    op.drop_column('users', 'membership_tier')
