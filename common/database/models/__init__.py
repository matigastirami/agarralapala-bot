from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from . import job_posting, candidate
