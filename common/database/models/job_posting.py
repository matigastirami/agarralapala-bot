from sqlalchemy import Column, Integer, String, DateTime, func, Text, UniqueConstraint
from . import Base

class JobPosting(Base):
    __tablename__ = 'job_postings'

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(length=128), nullable=False)
    company_name = Column(String(length=128), nullable=False)
    job_link = Column(String(length=512), nullable=False, unique=True)
    quick_description = Column(String(length=2048))

    company_type = Column(String(length=32), nullable=True)
    industry = Column(String(length=32), nullable=True)
    tech_stack = Column(String(length=256))
    stage = Column(String(length=16), nullable=True)
    
    # Enrichment fields
    detailed_description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    salary_range = Column(String(length=255), nullable=True)
    application_deadline = Column(DateTime, nullable=True)
    contact_info = Column(Text, nullable=True)
    enriched_at = Column(DateTime, nullable=True)