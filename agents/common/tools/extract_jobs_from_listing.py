from langchain_core.tools import tool
from playwright.sync_api import sync_playwright, Page
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import re
import logging
from urllib.parse import urljoin, urlparse
import time

class ExtractJobsInput(BaseModel):
    url: str = Field(description="The job listing page URL to extract jobs from")
    max_jobs: int = Field(description="Maximum number of jobs to extract", default=50)
    max_pages: int = Field(description="Maximum pages to crawl for listings", default=3)

class JobExtraction(BaseModel):
    url: str
    title: str
    company: str
    location: str = ""
    snippet: str = ""
    platform: str

# Platform-specific selectors
PLATFORM_SELECTORS = {
    "linkedin": {
        "job_cards": "[data-job-id], .job-search-card, .jobs-search-results__list-item",
        "job_link": "a[data-job-id], .job-search-card__link-wrapper a, a[href*='/jobs/view/']",
        "title": "[data-job-id] h3, .job-search-card__title a, .sr-only",
        "company": "[data-job-id] h4, .job-search-card__subtitle-primary a, .job-search-card__subtitle",
        "location": ".job-search-card__location, [data-job-id] .job-search-card__location",
        "next_button": "button[aria-label*='next'], .artdeco-pagination__button--next"
    },
    "indeed": {
        "job_cards": "[data-jk], .job_seen_beacon, .slider_container .slider_item",
        "job_link": "a[data-jk], .jobTitle a, h2 a[data-jk]",
        "title": ".jobTitle span, h2 span[data-testid='job-title']",
        "company": ".companyName span, [data-testid='company-name']",
        "location": ".companyLocation, [data-testid='job-location']",
        "next_button": "a[aria-label='Next Page'], [aria-label='Next']"
    },
    "glassdoor": {
        "job_cards": "[data-test='job-listing'], .react-job-listing",
        "job_link": "a[data-test='job-title'], .jobLink",
        "title": "[data-test='job-title'], .jobLink",
        "company": "[data-test='employer-name'], .employerName",
        "location": "[data-test='job-location'], .loc",
        "next_button": ".next, button[data-test='pagination-next']"
    },
    "angel": {
        "job_cards": "[data-test='JobSearchResult'], .job-listing",
        "job_link": "a[data-test='job-title-link'], .job-title a",
        "title": "[data-test='job-title-link'], .job-title",
        "company": "[data-test='company-name'], .company-name",
        "location": "[data-test='job-location'], .location",
        "next_button": "[data-test='pagination-next'], .next-page"
    },
    "greenhouse": {
        "job_cards": ".opening",
        "job_link": ".opening a",
        "title": ".opening a",
        "company": ".company-name, h1",
        "location": ".location",
        "next_button": ".next"
    },
    "lever": {
        "job_cards": ".posting",
        "job_link": ".posting a, .posting-title a",
        "title": ".posting-title, .posting a",
        "company": ".company-name, h1",
        "location": ".location, .posting-categories .location",
        "next_button": ".next"
    },
    "generic": {
        "job_cards": "[class*='job'], [class*='posting'], [class*='opening'], [class*='position'], [class*='listing']",
        "job_link": "a[href*='job'], a[href*='/jobs/'], a[href*='career'], a[href*='position']",
        "title": "h1, h2, h3, .title, [class*='title']",
        "company": ".company, [class*='company'], [class*='employer']",
        "location": ".location, [class*='location'], [class*='loc']",
        "next_button": "a:has-text('Next'), button:has-text('Next'), [class*='next'], [class*='pagination'] a:last-child"
    }
}

def detect_platform(url: str) -> str:
    """Detect platform from URL"""
    url_lower = url.lower()
    if "linkedin.com" in url_lower:
        return "linkedin"
    elif "indeed.com" in url_lower:
        return "indeed"
    elif "glassdoor.com" in url_lower:
        return "glassdoor"
    elif "angel.co" in url_lower or "wellfound.com" in url_lower:
        return "angel"
    elif "greenhouse.io" in url_lower:
        return "greenhouse"
    elif "lever.co" in url_lower:
        return "lever"
    else:
        return "generic"

def extract_job_links_from_page(page: Page, platform: str, base_url: str) -> List[Dict[str, Any]]:
    """Extract job links and metadata from a single page"""
    selectors = PLATFORM_SELECTORS.get(platform, PLATFORM_SELECTORS["generic"])
    jobs = []
    
    try:
        # Wait for job listings to load
        page.wait_for_selector(selectors["job_cards"], timeout=10000)
        
        # Get all job cards
        job_cards = page.locator(selectors["job_cards"])
        count = job_cards.count()
        
        logging.info(f"Found {count} job cards on {platform} page")
        
        for i in range(min(count, 50)):  # Limit to 50 jobs per page
            try:
                card = job_cards.nth(i)
                
                # Extract job link
                job_link_element = card.locator(selectors["job_link"]).first
                if job_link_element.count() == 0:
                    continue
                    
                href = job_link_element.get_attribute("href")
                if not href:
                    continue
                    
                # Make absolute URL
                job_url = urljoin(base_url, href)
                
                # Extract metadata
                title = ""
                try:
                    title_element = card.locator(selectors["title"]).first
                    if title_element.count() > 0:
                        title = title_element.inner_text().strip()
                except:
                    pass
                
                company = ""
                try:
                    company_element = card.locator(selectors["company"]).first  
                    if company_element.count() > 0:
                        company = company_element.inner_text().strip()
                except:
                    pass
                
                location = ""
                try:
                    location_element = card.locator(selectors["location"]).first
                    if location_element.count() > 0:
                        location = location_element.inner_text().strip()
                except:
                    pass
                
                # Get snippet if available
                snippet = ""
                try:
                    snippet = card.inner_text()[:200].strip()
                except:
                    pass
                
                jobs.append({
                    "url": job_url,
                    "title": title,
                    "company": company, 
                    "location": location,
                    "snippet": snippet,
                    "platform": platform
                })
                
            except Exception as e:
                logging.warning(f"Error extracting job {i}: {str(e)}")
                continue
                
    except Exception as e:
        logging.error(f"Error extracting jobs from page: {str(e)}")
    
    return jobs

def handle_pagination(page: Page, platform: str, max_pages: int) -> List[str]:
    """Handle pagination and return list of page URLs"""
    selectors = PLATFORM_SELECTORS.get(platform, PLATFORM_SELECTORS["generic"])
    page_urls = [page.url]
    
    for page_num in range(1, max_pages):
        try:
            # Look for next button
            next_button = page.locator(selectors["next_button"]).first
            
            if next_button.count() == 0:
                logging.info(f"No next button found, stopping at page {page_num}")
                break
                
            # Check if next button is disabled
            if next_button.get_attribute("disabled") or "disabled" in (next_button.get_attribute("class") or ""):
                logging.info(f"Next button disabled, stopping at page {page_num}")
                break
            
            # Click next button
            next_button.click()
            
            # Wait for page to load
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)  # Additional wait for dynamic content
            
            # Add new page URL if it's different
            current_url = page.url
            if current_url not in page_urls:
                page_urls.append(current_url)
            else:
                logging.info(f"Same URL after pagination, stopping at page {page_num}")
                break
                
        except Exception as e:
            logging.warning(f"Error during pagination on page {page_num}: {str(e)}")
            break
    
    return page_urls

@tool("extract_jobs_from_listing", args_schema=ExtractJobsInput)
def extract_jobs_from_listing(url: str, max_jobs: int = 50, max_pages: int = 3) -> List[Dict[str, Any]]:
    """
    Extract individual job URLs and metadata from a job listing page.
    Handles pagination automatically and supports major job boards and ATS platforms.
    """
    try:
        platform = detect_platform(url)
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        logging.info(f"Extracting jobs from {platform} listing: {url}")
        
        all_jobs = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            try:
                # Navigate to listing page
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Handle cookie banners and overlays
                try:
                    # Common cookie banner selectors
                    cookie_selectors = [
                        "button:has-text('Accept')",
                        "button:has-text('Allow')", 
                        "button:has-text('OK')",
                        "[data-test='accept-cookies']",
                        ".cookie-banner button"
                    ]
                    
                    for selector in cookie_selectors:
                        button = page.locator(selector).first
                        if button.count() > 0:
                            button.click()
                            break
                            
                    time.sleep(1)
                except:
                    pass
                
                # Extract jobs from first page
                jobs = extract_job_links_from_page(page, platform, base_url)
                all_jobs.extend(jobs)
                
                logging.info(f"Extracted {len(jobs)} jobs from first page")
                
                # Handle pagination if we need more jobs and haven't hit the limit
                if len(all_jobs) < max_jobs and max_pages > 1:
                    page_urls = handle_pagination(page, platform, max_pages)
                    
                    # Process additional pages
                    for page_url in page_urls[1:]:  # Skip first page (already processed)
                        if len(all_jobs) >= max_jobs:
                            break
                            
                        try:
                            logging.info(f"Processing additional page: {page_url}")
                            page.goto(page_url, wait_until="networkidle", timeout=20000)
                            
                            page_jobs = extract_job_links_from_page(page, platform, base_url)
                            all_jobs.extend(page_jobs)
                            
                            logging.info(f"Extracted {len(page_jobs)} jobs from additional page")
                            
                        except Exception as e:
                            logging.warning(f"Error processing page {page_url}: {str(e)}")
                            continue
                
                # Remove duplicates based on URL
                seen_urls = set()
                unique_jobs = []
                for job in all_jobs[:max_jobs]:  # Limit to max_jobs
                    if job["url"] not in seen_urls:
                        seen_urls.add(job["url"])
                        unique_jobs.append(job)
                
                logging.info(f"Final extraction: {len(unique_jobs)} unique jobs from {platform}")
                return unique_jobs
                
            finally:
                browser.close()
                
    except Exception as e:
        logging.error(f"Error extracting jobs from listing {url}: {str(e)}")
        return []