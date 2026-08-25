"""foundation meta

Revision ID: 20260825_0001
Revises:
Create Date: 2026-08-25

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260825_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "foundation_meta",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_foundation_meta_label", "foundation_meta", ["label"])


def downgrade() -> None:
    op.drop_index("ix_foundation_meta_label", table_name="foundation_meta")
    op.drop_table("foundation_meta")
