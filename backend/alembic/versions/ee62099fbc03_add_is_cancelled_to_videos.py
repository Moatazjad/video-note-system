"""add is_cancelled to videos

Revision ID: ee62099fbc03
Revises: d6568996f9f2
Create Date: 2026-02-24
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ee62099fbc03"
down_revision: Union[str, Sequence[str], None] = "d6568996f9f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "videos",
        sa.Column(
            "is_cancelled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("videos", "is_cancelled")