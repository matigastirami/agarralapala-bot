"""add_unique_constraints_for_upsert

Revision ID: 854a9eb89f00
Revises: dc4be968c73b
Create Date: 2025-08-13 23:29:14.296647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '854a9eb89f00'
down_revision: Union[str, Sequence[str], None] = 'dc4be968c73b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint on job_link for job_postings table
    op.create_unique_constraint('uq_job_postings_job_link', 'job_postings', ['job_link'])
    
    # Add composite unique constraint on candidate_id + job_posting_id for matches table
    op.create_unique_constraint('uq_matches_candidate_job', 'matches', ['candidate_id', 'job_posting_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove unique constraints
    op.drop_constraint('uq_job_postings_job_link', 'job_postings', type_='unique')
    op.drop_constraint('uq_matches_candidate_job', 'matches', type_='unique')
