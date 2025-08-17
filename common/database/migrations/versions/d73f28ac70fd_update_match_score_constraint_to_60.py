"""update_match_score_constraint_to_60

Revision ID: d73f28ac70fd
Revises: e1ca08f968ae
Create Date: 2025-08-17 00:45:23.730720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd73f28ac70fd'
down_revision: Union[str, Sequence[str], None] = 'e1ca08f968ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old constraint and create new one with 60% threshold
    op.drop_constraint('chk_match_score_minimum', 'matches', type_='check')
    op.create_check_constraint(
        'chk_match_score_minimum',
        'matches',
        'match_score >= 60.0'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert back to 80% threshold
    op.drop_constraint('chk_match_score_minimum', 'matches', type_='check')
    op.create_check_constraint(
        'chk_match_score_minimum',
        'matches',
        'match_score >= 80.0'
    )
