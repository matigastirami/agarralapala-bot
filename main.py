
from agents.job_seeker.agent import exec_jobs_agent
from common.database.repositories.job_posting import JobPostingsRepository
import sys

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        raise Exception('You must enter a prompt')
    message = sys.argv[1]
    job_postings = exec_jobs_agent(user_input=message)
    job_postings_repo = JobPostingsRepository()
    job_postings_repo.save_job_postings(job_postings)
