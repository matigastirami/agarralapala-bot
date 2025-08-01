from sqlalchemy import Column, Integer, String, Float, func, DateTime

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