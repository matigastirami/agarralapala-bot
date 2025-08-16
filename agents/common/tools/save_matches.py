from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional, List

from common.database.repositories.matches import MatchesRepository

class SaveJobMatchesInput(BaseModel):
    job_matches: Optional[List[dict]] = Field(description="The list of job matches dicts to upsert into the DB", default=[])

@tool('save_job_matches', args_schema=SaveJobMatchesInput)
def save_job_matches(*, job_matches: Optional[List[dict]]):
    """
    Upserts the job matches into the DB, receives a list of dicts.
    Will update existing matches (by candidate_id + job_posting_id) or insert new ones.
    """
    # Handle None values
    if job_matches is None:
        job_matches = []
    
    if not job_matches:
        return "No job matches to save."
    
    try:
        matches_repo = MatchesRepository()
        matches_repo.save_matches(job_matches)
        return f"Successfully upserted {len(job_matches)} job matches"
    except Exception as e:
        return f"Error upserting job matches: {str(e)}"