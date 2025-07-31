from common.database.models.job_posting import JobPosting
from common.database.database import db_session

from sqlalchemy.exc import IntegrityError

class JobPostingsRepository():
    def __init__(self) -> None:
        self.session = db_session()

    def save_job_postings(self, jobs_list: list[dict]):
        print(jobs_list)
        for job in jobs_list:
            job_obj = JobPosting(**job)
            self.session.add(job_obj)

        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
        finally:
            self.session.close()

    def get_job_postings(self):
        return self.session.query(JobPosting).all()
