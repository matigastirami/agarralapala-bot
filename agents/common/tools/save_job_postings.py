from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, List

from common.database.repositories.job_posting import JobPostingsRepository

class SaveJobPostingsInput(BaseModel):
    job_postings: Optional[List[dict]] = Field(description="The list of job postings dicts to upsert into the DB", default=[])

@tool('save_job_postings', args_schema=SaveJobPostingsInput)
def save_job_postings(*, job_postings: Optional[List[dict]] = []):
    """
    Upserts the job postings into the DB, receives a list of dicts.
    Will update existing job postings (by job_link) or insert new ones.
    """
    # Handle None values
    if job_postings is None:
        job_postings = []
    
    if not job_postings:
        return "No job postings to save."
    
    try:
        job_postings_repo = JobPostingsRepository()
        job_postings_repo.save_job_postings(job_postings)
        return f"Successfully upserted {len(job_postings)} job postings"
    except Exception as e:
        return f"Error upserting job postings: {str(e)}"
