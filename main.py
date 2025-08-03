import logging
import time

from agents.job_seeker.agent import exec_jobs_agent
from common.database.repositories.job_posting import JobPostingsRepository
import sys

from crons.cron_manager import CronManager
from crons.job_seeker_cron import JobSeekerCron

# if __name__ == '__main__':
#     if len(sys.argv) <= 1:
#         raise Exception('You must enter a prompt')
#     message = sys.argv[1]
#     job_postings = exec_jobs_agent(user_input=message)
#     job_postings_repo = JobPostingsRepository()
#     job_postings_repo.save_job_postings(job_postings)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    cron_manager = CronManager()
    cron_manager.register(JobSeekerCron())
    cron_manager.start()

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        cron_manager.shutdown()
