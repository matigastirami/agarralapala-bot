"""default_created_at_candidates

Revision ID: 556d24ac2c86
Revises: 41f2aa130087
Create Date: 2025-08-03 16:24:13.084222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '556d24ac2c86'
down_revision: Union[str, Sequence[str], None] = '41f2aa130087'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set default to now()
    op.alter_column(
        "candidates",
        "created_at",
        server_default=sa.text("now()"),
        existing_type=sa.TIMESTAMP(timezone=True),
        existing_nullable=False
    )


def downgrade() -> None:
    # Remove default
    op.alter_column(
        "candidates",
        "created_at",
        server_default=None,
        existing_type=sa.TIMESTAMP(timezone=True),
        existing_nullable=False
    )
