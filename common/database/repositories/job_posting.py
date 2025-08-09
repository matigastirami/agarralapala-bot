from common.database.models.job_posting import JobPosting
from common.database.database import db_session
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError

class JobPostingsRepository:
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
    
    def get_job_postings_by_ids(self, job_ids: List[int]):
        """Get job postings by a list of IDs"""
        return self.session.query(JobPosting).filter(JobPosting.id.in_(job_ids)).all()
    
    def get_job_postings_without_details(self):
        """Get job postings that don't have detailed descriptions yet"""
        return self.session.query(JobPosting).filter(
            JobPosting.detailed_description.is_(None)
        ).all()
    
    def update_job_details(self, job_id: int, detailed_description: str = None, 
                          requirements: str = None, benefits: str = None,
                          salary_range: str = None, application_deadline: datetime = None,
                          contact_info: str = None):
        """Update job posting with enriched details"""
        try:
            job = self.session.query(JobPosting).filter(JobPosting.id == job_id).first()
            if job:
                if detailed_description is not None:
                    job.detailed_description = detailed_description
                if requirements is not None:
                    job.requirements = requirements
                if benefits is not None:
                    job.benefits = benefits
                if salary_range is not None:
                    job.salary_range = salary_range
                if application_deadline is not None:
                    job.application_deadline = application_deadline
                if contact_info is not None:
                    job.contact_info = contact_info
                
                job.enriched_at = datetime.now()
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()
