"""add_default_timestamp_candidate

Revision ID: 75b988ce2af9
Revises: 006f081c40e7
Create Date: 2025-07-31 09:10:36.090946

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75b988ce2af9'
down_revision: Union[str, Sequence[str], None] = '006f081c40e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'candidates',
        'created_at',
        server_default=None,
        existing_type=sa.DateTime(),
        nullable=False,
    )
