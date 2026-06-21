"""create leads table

Revision ID: 20260621_0001
Revises:
Create Date: 2026-06-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260621_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "source",
            sa.Enum("WEBSITE", "GITHUB", "CV", "TELEGRAM", "KWORK", "OTHER", name="leadsource"),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.Enum(
                "JOB_OFFER",
                "PROJECT_REQUEST",
                "PARTNERSHIP",
                "SUPPORT",
                "SPAM",
                "OTHER",
                name="leadcategory",
            ),
            nullable=False,
        ),
        sa.Column(
            "sentiment",
            sa.Enum("POSITIVE", "NEUTRAL", "NEGATIVE", name="leadsentiment"),
            nullable=False,
        ),
        sa.Column("ai_reply", sa.Text(), nullable=False),
        sa.Column("email_sent", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leads_email"), "leads", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leads_email"), table_name="leads")
    op.drop_table("leads")
