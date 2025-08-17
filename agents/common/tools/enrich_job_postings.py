from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
import logging
from typing import List, Dict, Any, Optional, Union
from common.database.repositories.job_posting import JobPostingsRepository
from datetime import datetime

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
                    page.goto(job.job_link, wait_until="networkidle", timeout=30000)
                    
                    # Check if job is still available
                    job_status = check_job_availability(page, job.job_link)
                    
                    if job_status['status'] == 'expired':
                        logging.warning(f"Job {job_id} is expired/filled: {job_status['reason']}")
                        # Update database to mark job as expired
                        job_postings_repo.update_job_status(job_id, 'expired')
                        enriched_jobs.append({
                            "id": job_id,
                            "job_title": job_title,
                            "company_name": company_name,
                            "enriched": False,
                            "status": "expired",
                            "reason": job_status['reason']
                        })
                        continue
                    
                    # Extract detailed information
                    job_details = extract_job_details(page, job.job_link)
                    
                    # Update database with enriched data
                    job_postings_repo.update_job_details(
                        job_id=job_id,
                        detailed_description=job_details.get('description', ''),
                        requirements=job_details.get('requirements', ''),
                        benefits=job_details.get('benefits', ''),
                        salary_range=job_details.get('salary_range', ''),
                        application_deadline=job_details.get('deadline') if job_details.get('deadline') else None,
                        contact_info=job_details.get('contact_info', ''),
                        status='active'
                    )
                    
                    enriched_jobs.append({
                        "id": job_id,
                        "job_title": job_title,
                        "company_name": company_name,
                        "enriched": True,
                        "status": "active",
                        "details": job_details
                    })
                    
                except Exception as e:
                    # Use stored attributes to avoid session issues
                    job_id = getattr(job, 'id', 'unknown')
                    job_title = getattr(job, 'job_title', 'unknown')
                    company_name = getattr(job, 'company_name', 'unknown')
                    
                    logging.error(f"Error enriching job {job_id}: {str(e)}")
                    # Update database to mark job as error
                    try:
                        job_postings_repo.update_job_status(job_id, 'error')
                    except:
                        pass
                    
                    enriched_jobs.append({
                        "id": job_id,
                        "job_title": job_title,
                        "company_name": company_name,
                        "enriched": False,
                        "status": "error",
                        "error": str(e)
                    })
            
            browser.close()
        
        return enriched_jobs
        
    finally:
        # Ensure session is closed
        job_postings_repo.close_session()

def check_job_availability(page, job_url: str) -> Dict[str, str]:
    """
    Check if a job posting is still available or has been filled/expired.
    Returns a dict with 'status' ('active' or 'expired') and 'reason'.
    """
    try:
        # Get page content and title
        page_content = page.content().lower()
        page_title = page.title().lower()
        
        # LinkedIn patterns - check for specific LinkedIn job posting indicators
        if 'linkedin.com/jobs/view' in job_url or 'linkedin.com/jobs/collections' in job_url:
            logging.info(f"Checking LinkedIn job availability for URL: {job_url}")
            
            # LinkedIn specific patterns for expired/filled jobs
            linkedin_expired_patterns = [
                'no longer accepting applications',
                'no longer accepting',
                'applications are no longer being accepted',
                'this position is no longer accepting applications',
                'this job is no longer accepting applications',
                'position has been filled',
                'this position has been filled',
                'job has been filled',
                'this job has been filled',
                'position is no longer available',
                'this position is no longer available',
                'job is no longer available',
                'this job is no longer available',
                'position has been closed',
                'this position has been closed',
                'job has been closed',
                'this job has been closed',
                'position has expired',
                'this position has expired',
                'job has expired',
                'this job has expired',
                'this position is closed',
                'this job is closed',
                'position closed',
                'job closed',
                'applications closed',
                'this position is no longer accepting',
                'this job is no longer accepting',
                'position no longer accepting',
                'job no longer accepting'
            ]
            
            for pattern in linkedin_expired_patterns:
                if pattern in page_content:
                    logging.info(f"LinkedIn job detected as expired with pattern: {pattern}")
                    return {'status': 'expired', 'reason': f'LinkedIn job expired: {pattern}'}
            
            # Check for LinkedIn search results page (not a specific job)
            if ('empleos' in job_url or 'jobs' in job_url) and 'view' not in job_url:
                return {'status': 'expired', 'reason': 'LinkedIn search results page, not a specific job posting'}
            
            # Check if it's a LinkedIn job posting page by looking for common elements
            job_elements = page.query_selector_all('[data-job-id], .job-view-layout, .job-details-jobs-unified-top-card')
            if not job_elements:
                return {'status': 'expired', 'reason': 'Not a valid LinkedIn job posting page'}
        
        # Ashby patterns
        elif 'jobs.ashbyhq.com' in job_url:
            if 'job not found' in page_content or 'job not found' in page_title:
                return {'status': 'expired', 'reason': 'Job not found (Ashby)'}
            if 'this position has been filled' in page_content:
                return {'status': 'expired', 'reason': 'Position filled (Ashby)'}
        
        # Startup.jobs patterns
        elif 'startup.jobs' in job_url:
            if 'this job is no longer available' in page_content:
                return {'status': 'expired', 'reason': 'Job no longer available (Startup.jobs)'}
            if 'position has been filled' in page_content:
                return {'status': 'expired', 'reason': 'Position filled (Startup.jobs)'}
        
        # Lever patterns
        elif 'jobs.lever.co' in job_url:
            if 'this position has been filled' in page_content:
                return {'status': 'expired', 'reason': 'Position filled (Lever)'}
            if 'this job is no longer available' in page_content:
                return {'status': 'expired', 'reason': 'Job no longer available (Lever)'}
            if '404' in page_title or 'not found' in page_title:
                return {'status': 'expired', 'reason': 'Job not found (Lever)'}
        
        # Greenhouse patterns
        elif 'boards.greenhouse.io' in job_url or 'jobs.greenhouse.io' in job_url:
            if 'this position has been filled' in page_content:
                return {'status': 'expired', 'reason': 'Position filled (Greenhouse)'}
            if 'this job is no longer available' in page_content:
                return {'status': 'expired', 'reason': 'Job no longer available (Greenhouse)'}
            if '404' in page_title or 'not found' in page_title:
                return {'status': 'expired', 'reason': 'Job not found (Greenhouse)'}
        
        # Generic patterns that work across multiple platforms
        expired_patterns = [
            'this position has been filled',
            'this job is no longer available',
            'position has been filled',
            'job has been filled',
            'this opportunity is no longer available',
            'position is no longer available',
            'job posting has expired',
            'this posting has been removed',
            'position has been closed',
            'job has been closed',
            '404',
            'not found',
            'page not found',
            'job not found',
            'position not found'
        ]
        
        for pattern in expired_patterns:
            if pattern in page_content or pattern in page_title:
                return {'status': 'expired', 'reason': f'Job expired/filled: {pattern}'}
        
        # Check if page has meaningful content (not just error pages)
        if len(page_content) < 100:  # Very short content might indicate an error page
            return {'status': 'expired', 'reason': 'Page has insufficient content'}
        
        # For LinkedIn jobs, add specific logging
        if 'linkedin.com/jobs/view' in job_url or 'linkedin.com/jobs/collections' in job_url:
            logging.info(f"LinkedIn job appears to be active")
        
        return {'status': 'active', 'reason': 'Job appears to be active'}
        
    except Exception as e:
        logging.error(f"Error checking job availability: {str(e)}")
        return {'status': 'error', 'reason': f'Error checking availability: {str(e)}'}

def extract_job_details(page, job_url: str):
    """
    Extract detailed job information from the page.
    Enhanced implementation with platform-specific selectors.
    """
    try:
        # Platform-specific selectors
        if 'linkedin.com/jobs/view' in job_url or 'linkedin.com/jobs/collections' in job_url:
            return extract_linkedin_details(page)
        elif 'jobs.ashbyhq.com' in job_url:
            return extract_ashby_details(page)
        elif 'startup.jobs' in job_url:
            return extract_startup_jobs_details(page)
        elif 'jobs.lever.co' in job_url:
            return extract_lever_details(page)
        elif 'boards.greenhouse.io' in job_url or 'jobs.greenhouse.io' in job_url:
            return extract_greenhouse_details(page)
        else:
            return extract_generic_details(page)
            
    except Exception as e:
        logging.error(f"Error extracting job details: {str(e)}")
        return {}

def extract_ashby_details(page):
    """Extract job details from Ashby job pages"""
    try:
        # Ashby-specific selectors
        description = page.query_selector('[data-testid="job-description"], .job-description, .description')
        requirements = page.query_selector('[data-testid="requirements"], .requirements, .qualifications')
        benefits = page.query_selector('[data-testid="benefits"], .benefits, .perks')
        salary = page.query_selector('[data-testid="salary"], .salary, .compensation')
        
        return {
            "description": description.inner_text() if description else "",
            "requirements": requirements.inner_text() if requirements else "",
            "benefits": benefits.inner_text() if benefits else "",
            "salary_range": salary.inner_text() if salary else "",
            "deadline": None,
            "contact_info": None
        }
    except Exception as e:
        logging.error(f"Error extracting Ashby details: {str(e)}")
        return {}

def extract_startup_jobs_details(page):
    """Extract job details from Startup.jobs pages"""
    try:
        description = page.query_selector('.job-description, .description, [class*="description"]')
        requirements = page.query_selector('.requirements, .qualifications, [class*="requirement"]')
        benefits = page.query_selector('.benefits, .perks, [class*="benefit"]')
        salary = page.query_selector('.salary, .compensation, [class*="salary"]')
        
        return {
            "description": description.inner_text() if description else "",
            "requirements": requirements.inner_text() if requirements else "",
            "benefits": benefits.inner_text() if benefits else "",
            "salary_range": salary.inner_text() if salary else "",
            "deadline": None,
            "contact_info": None
        }
    except Exception as e:
        logging.error(f"Error extracting Startup.jobs details: {str(e)}")
        return {}

def extract_lever_details(page):
    """Extract job details from Lever job pages"""
    try:
        description = page.query_selector('.posting-content, .job-description, .description')
        requirements = page.query_selector('.requirements, .qualifications, [class*="requirement"]')
        benefits = page.query_selector('.benefits, .perks, [class*="benefit"]')
        salary = page.query_selector('.salary, .compensation, [class*="salary"]')
        
        return {
            "description": description.inner_text() if description else "",
            "requirements": requirements.inner_text() if requirements else "",
            "benefits": benefits.inner_text() if benefits else "",
            "salary_range": salary.inner_text() if salary else "",
            "deadline": None,
            "contact_info": None
        }
    except Exception as e:
        logging.error(f"Error extracting Lever details: {str(e)}")
        return {}

def extract_greenhouse_details(page):
    """Extract job details from Greenhouse job pages"""
    try:
        description = page.query_selector('.job-description, .description, [class*="description"]')
        requirements = page.query_selector('.requirements, .qualifications, [class*="requirement"]')
        benefits = page.query_selector('.benefits, .perks, [class*="benefit"]')
        salary = page.query_selector('.salary, .compensation, [class*="salary"]')
        
        return {
            "description": description.inner_text() if description else "",
            "requirements": requirements.inner_text() if requirements else "",
            "benefits": benefits.inner_text() if benefits else "",
            "salary_range": salary.inner_text() if salary else "",
            "deadline": None,
            "contact_info": None
        }
    except Exception as e:
        logging.error(f"Error extracting Greenhouse details: {str(e)}")
        return {}

def extract_linkedin_details(page):
    """Extract job details from LinkedIn job pages"""
    try:
        # LinkedIn-specific selectors for job details
        # Job description is usually in a specific container
        description = page.query_selector('.job-description__text, .show-more-less-html__markup, [data-job-description], .description__text')
        
        # Requirements might be in a separate section
        requirements = page.query_selector('.job-criteria-item, .job-criteria-text, [data-testid="job-criteria"], .qualifications')
        
        # Benefits are often mentioned in the description or separate sections
        benefits = page.query_selector('.benefits, .perks, [data-testid="benefits"], .job-benefits')
        
        # Salary information (LinkedIn often doesn't show this prominently)
        salary = page.query_selector('.salary, .compensation, [data-testid="salary"], .job-salary')
        
        # Contact information (usually not available on LinkedIn job pages)
        contact_info = page.query_selector('.contact-info, .company-contact, [data-testid="contact"]')
        
        # If description is not found with specific selectors, try to get the main content
        if not description:
            description = page.query_selector('main, .main-content, .job-content, [role="main"]')
        
        return {
            "description": description.inner_text() if description else "",
            "requirements": requirements.inner_text() if requirements else "",
            "benefits": benefits.inner_text() if benefits else "",
            "salary_range": salary.inner_text() if salary else "",
            "deadline": None,  # LinkedIn usually doesn't show application deadlines
            "contact_info": contact_info.inner_text() if contact_info else ""
        }
    except Exception as e:
        logging.error(f"Error extracting LinkedIn details: {str(e)}")
        return {}

def extract_generic_details(page):
    """Generic extraction for unknown job platforms"""
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
        logging.error(f"Error extracting generic job details: {str(e)}")
        return {}
