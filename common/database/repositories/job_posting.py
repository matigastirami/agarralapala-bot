from common.database.models.job_posting import JobPosting
from common.database.database import db_session
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError

class JobPostingsRepository:
    def __init__(self) -> None:
        self.session = db_session()

    def save_job_postings(self, jobs_list: list[dict]):
        """
        Upsert job postings - update if exists (by job_link), insert if new
        """
        print(f"Upserting {len(jobs_list)} job postings")
        
        successful_upserts = 0
        failed_upserts = 0
        
        for job_data in jobs_list:
            try:
                # Check if job posting already exists by job_link
                existing_job = self.session.query(JobPosting).filter(
                    JobPosting.job_link == job_data['job_link']
                ).first()
                
                if existing_job:
                    # Update existing job posting
                    print(f"Updating existing job: {job_data['job_title']} at {job_data['company_name']}")
                    for key, value in job_data.items():
                        if hasattr(existing_job, key):
                            setattr(existing_job, key, value)
                else:
                    # Insert new job posting
                    print(f"Inserting new job: {job_data['job_title']} at {job_data['company_name']}")
                    job_obj = JobPosting(**job_data)
                    self.session.add(job_obj)
                
                # Commit each job individually to avoid transaction conflicts
                self.session.commit()
                successful_upserts += 1
                
            except Exception as e:
                print(f"Error processing job {job_data.get('job_title', 'Unknown')}: {e}")
                self.session.rollback()
                failed_upserts += 1
                continue

        print(f"Successfully upserted {successful_upserts} job postings, {failed_upserts} failed")
        
        if failed_upserts > 0:
            raise Exception(f"Failed to upsert {failed_upserts} job postings")
        
        self.session.close()

    def upsert_job_posting(self, job_data: dict):
        """
        Upsert a single job posting
        """
        try:
            existing_job = self.session.query(JobPosting).filter(
                JobPosting.job_link == job_data['job_link']
            ).first()
            
            if existing_job:
                # Update existing job posting
                for key, value in job_data.items():
                    if hasattr(existing_job, key):
                        setattr(existing_job, key, value)
                print(f"Updated job: {job_data['job_title']}")
            else:
                # Insert new job posting
                job_obj = JobPosting(**job_data)
                self.session.add(job_obj)
                print(f"Inserted new job: {job_data['job_title']}")
            
            self.session.commit()
            return existing_job or job_obj
            
        except Exception as e:
            self.session.rollback()
            raise e

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
        # Don't close session here - let the caller manage it
    
    def get_by_id(self, job_id: int):
        """Get a single job posting by ID"""
        try:
            return self.session.query(JobPosting).filter(JobPosting.id == job_id).first()
        except Exception as e:
            self.session.rollback()
            raise e
        # Don't close session here - let the caller manage it

    def get_by_job_link(self, job_link: str):
        """Get a single job posting by job_link"""
        try:
            return self.session.query(JobPosting).filter(JobPosting.job_link == job_link).first()
        except Exception as e:
            self.session.rollback()
            raise e
        # Don't close session here - let the caller manage it

    def exists_by_job_link(self, job_link: str) -> bool:
        """Check if a job posting exists by job_link"""
        try:
            return self.session.query(JobPosting).filter(JobPosting.job_link == job_link).first() is not None
        except Exception as e:
            self.session.rollback()
            raise e
        # Don't close session here - let the caller manage it

    def close_session(self):
        """Close the session - call this when done with the repository"""
        if self.session:
            self.session.close()