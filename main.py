
from agents.job_seeker.agent import exec_jobs_agent
from repositories.job_posting import JobPostingsRepository
import sys
import common.config

if __name__ == '__main__':
    message = sys.argv[1]
    if not message or len(message) == 0:
        raise Exception('You must enter a prompt')
    job_postings = exec_jobs_agent(user_input=message)
    job_postings_repo = JobPostingsRepository()
    job_postings_repo.save_job_postings(job_postings)
