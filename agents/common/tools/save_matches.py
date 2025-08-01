from langchain_core.tools import tool
from pydantic import BaseModel, Field

from common.database.repositories.matches import MatchesRepository

class SaveJobMatchesInput(BaseModel):
    job_matches: list[dict] = Field(description="The list of job matches to insert into the DB", default=[])

@tool('save_job_matches', args_schema=SaveJobMatchesInput)
def save_job_matches(job_matches: list[dict]):
    """
    Saves the job matches into the DB
    """
    matches_repo = MatchesRepository()
    return matches_repo.save_matches(job_matches)