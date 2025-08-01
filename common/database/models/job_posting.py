from sqlalchemy import Column, Integer, String, DateTime, func
from . import Base

class JobPosting(Base):
    __tablename__ = 'job_postings'

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(length=128), nullable=False)
    company_name = Column(String(length=128), nullable=False)
    job_link = Column(String(length=512), nullable=False)
    quick_description = Column(String(length=2048))

    company_type = Column(String(length=32), nullable=True)
    industry = Column(String(length=32), nullable=True)
    tech_stack = Column(String(length=256))
    stage = Column(String(length=16), nullable=True)