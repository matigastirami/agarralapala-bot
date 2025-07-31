from langchain_core.tools import tool

from common.database.repositories.job_posting import JobPostingsRepository

@tool('get_job_postings')
def get_job_postings():
    """
    Returns all the job postings from the database
    """
    job_postings_repo = JobPostingsRepository()
    return job_postings_repo.get_job_postings()