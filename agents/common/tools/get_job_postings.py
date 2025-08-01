from langchain_core.tools import tool

from common.database.repositories.job_posting import JobPostingsRepository

@tool('get_job_postings')
def get_job_postings():
    """
    Returns all the job postings from the database
    """
    job_postings_repo = JobPostingsRepository()
    job_postings = job_postings_repo.get_job_postings()
    return [
        {
            "id": r.id,
            "job_title": r.job_title,
            "company_name": r.company_name,
            "job_link": r.job_link,
            "quick_description": r.quick_description,
            "company_type": r.company_type,
            "industry": r.industry,
            "tech_stack": r.tech_stack,
            "stage": r.stage,
        }
        for r in job_postings
    ]