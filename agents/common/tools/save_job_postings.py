from langchain_core.tools import tool
from pydantic import BaseModel, Field

from common.database.repositories.job_posting import JobPostingsRepository

class SaveJobPostingsInput(BaseModel):
    job_postings: list[dict] = Field(description="The list of job postings dicts to insert into the DB", default=[])

@tool('save_job_postings', args_schema=SaveJobPostingsInput)
def save_job_postings(*, job_postings: list[dict] = []):
    """
    Saves the job postings into the DB, receives a list of dicts
    """
    if job_postings is None:
        raise ValueError("Tool called without 'job_postings' argument.")
    job_postings_repo = JobPostingsRepository()
    job_postings_repo.save_job_postings(job_postings)
