from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
import logging
from typing import List, Dict, Any, Optional, Union
from common.database.repositories.job_posting import JobPostingsRepository

@tool('enrich_job_postings')
def enrich_job_postings(job_ids: Any = None) -> List[Dict[str, Any]]:
    """
    Fetches detailed job descriptions for job postings using Playwright.
    If job_ids is not provided, fetches all job postings that don't have detailed descriptions.
    """
    # Handle various input types
    if job_ids is None:
        job_ids = []
    elif not isinstance(job_ids, list):
        job_ids = []
    
    job_postings_repo = JobPostingsRepository()
    
    try:
        # Get job postings to enrich
        if job_ids:
            job_postings = job_postings_repo.get_job_postings_by_ids(job_ids)
        else:
            # Get job postings without detailed descriptions
            job_postings = job_postings_repo.get_job_postings_without_details()
        
        enriched_jobs = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            for job in job_postings:
                try:
                    # Store job attributes before any session operations
                    job_id = job.id
                    job_title = job.job_title
                    company_name = job.company_name
                    
                    logging.info(f"Enriching job posting {job_id}: {job_title}")
                    
                    # Navigate to job posting URL
                    page.goto(job.job_link, wait_until="networkidle")
                    
                    # Extract detailed information
                    job_details = extract_job_details(page)
                    
                    # Update database with enriched data
                    job_postings_repo.update_job_details(
                        job_id=job_id,
                        detailed_description=job_details.get('description', ''),
                        requirements=job_details.get('requirements', ''),
                        benefits=job_details.get('benefits', ''),
                        salary_range=job_details.get('salary_range', ''),
                        application_deadline=job_details.get('deadline') if job_details.get('deadline') else None,
                        contact_info=job_details.get('contact_info', '')
                    )
                    
                    enriched_jobs.append({
                        "id": job_id,
                        "job_title": job_title,
                        "company_name": company_name,
                        "enriched": True,
                        "details": job_details
                    })
                    
                except Exception as e:
                    # Use stored attributes to avoid session issues
                    job_id = getattr(job, 'id', 'unknown')
                    job_title = getattr(job, 'job_title', 'unknown')
                    company_name = getattr(job, 'company_name', 'unknown')
                    
                    logging.error(f"Error enriching job {job_id}: {str(e)}")
                    enriched_jobs.append({
                        "id": job_id,
                        "job_title": job_title,
                        "company_name": company_name,
                        "enriched": False,
                        "error": str(e)
                    })
            
            browser.close()
        
        return enriched_jobs
        
    finally:
        # Ensure session is closed
        job_postings_repo.close_session()

def extract_job_details(page):
    """
    Extract detailed job information from the page.
    This is a generic implementation - you might need to customize based on job sites.
    """
    try:
        # Generic selectors - adjust based on target job sites
        description = page.query_selector('[data-testid="job-description"], .job-description, .description, [class*="description"]')
        requirements = page.query_selector('[data-testid="requirements"], .requirements, .qualifications, [class*="requirement"]')
        benefits = page.query_selector('[data-testid="benefits"], .benefits, .perks, [class*="benefit"]')
        salary = page.query_selector('[data-testid="salary"], .salary, .compensation, [class*="salary"]')
        
        return {
            "description": description.inner_text() if description else "",
            "requirements": requirements.inner_text() if requirements else "",
            "benefits": benefits.inner_text() if benefits else "",
            "salary_range": salary.inner_text() if salary else "",
            "deadline": None,
            "contact_info": None
        }
    except Exception as e:
        logging.error(f"Error extracting job details: {str(e)}")
        return {}
