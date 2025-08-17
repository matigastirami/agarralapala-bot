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
    Only saves matches with a score of 60% or higher.
    """
    # Handle None values
    if job_matches is None:
        job_matches = []
    
    if not job_matches:
        return "No job matches to save."
    
    # Filter out matches with score below 60%
    high_quality_matches = []
    filtered_out_count = 0
    
    for match in job_matches:
        match_score = match.get('match_score', 0)
        if match_score >= 60.0:
            high_quality_matches.append(match)
        else:
            filtered_out_count += 1
    
    if filtered_out_count > 0:
        print(f"Filtered out {filtered_out_count} matches with score below 60%")
    
    if not high_quality_matches:
        return f"No high-quality matches (score >= 60%) to save. Filtered out {filtered_out_count} low-quality matches."
    
    try:
        matches_repo = MatchesRepository()
        matches_repo.save_matches(high_quality_matches)
        return f"Successfully upserted {len(high_quality_matches)} high-quality job matches (filtered out {filtered_out_count} low-quality matches)"
    except Exception as e:
        return f"Error upserting job matches: {str(e)}"