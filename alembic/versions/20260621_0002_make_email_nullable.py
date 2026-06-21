"""make lead email nullable

Revision ID: 20260621_0002
Revises: 20260621_0001
Create Date: 2026-06-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260621_0002"
down_revision: str | None = "20260621_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "leads",
        "email",
        existing_type=sa.String(length=254),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "leads",
        "email",
        existing_type=sa.String(length=254),
        nullable=False,
    )
