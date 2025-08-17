from sqlalchemy import Column, Integer, String, Float, func, DateTime, UniqueConstraint, CheckConstraint

from common.database.models import Base


class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=False)
    job_posting_id = Column(Integer, nullable=False)
    match_score = Column(Float, nullable=False)
    strengths = Column(String(length=1024), nullable=True)
    weaknesses = Column(String(length=1024), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    notified_at = Column(DateTime, nullable=True)
    
    # Composite unique constraint to prevent duplicate matches
    # Check constraint to ensure only quality matches (score >= 60)
    __table_args__ = (
        UniqueConstraint('candidate_id', 'job_posting_id', name='uq_matches_candidate_job'),
        CheckConstraint('match_score >= 60.0', name='chk_match_score_minimum'),
    )