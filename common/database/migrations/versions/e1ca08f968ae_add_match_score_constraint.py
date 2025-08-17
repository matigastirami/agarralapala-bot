"""add_match_score_constraint

Revision ID: e1ca08f968ae
Revises: e5996f28c4f1
Create Date: 2025-08-17 00:37:53.730720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1ca08f968ae'
down_revision: Union[str, Sequence[str], None] = 'e5996f28c4f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add check constraint to ensure only high-quality matches (score >= 80) are stored
    op.create_check_constraint(
        'chk_match_score_minimum',
        'matches',
        'match_score >= 80.0'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the check constraint
    op.drop_constraint('chk_match_score_minimum', 'matches', type_='check')
