from langchain_core.tools import tool
from playwright.sync_api import sync_playwright, Page
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Literal
import re
import logging
from urllib.parse import urlparse, parse_qs

from .job_discovery_cache import get_cached_url_analysis, cache_url_analysis

class AnalyzeUrlInput(BaseModel):
    url: str = Field(description="The URL to analyze")

class UrlAnalysisResult(BaseModel):
    url: str
    type: Literal["direct_job", "job_listing", "company_careers", "not_relevant"]
    confidence: float
    platform: str
    reason: str
    metadata: Dict[str, Any] = {}

# URL patterns for known job boards and ATS systems
JOB_PATTERNS = {
    # Direct job posting patterns
    "direct_job": [
        r"greenhouse\.io/jobs/\d+",
        r"lever\.co/.*/.+",
        r"ashbyhq\.com/.*/jobs/.*",
        r"workday\.com/.*/job/.*",
        r"smartrecruiters\.com/.*/jobs/.*",
        r"bamboohr\.com/.*/jobs/.*",
        r"jobvite\.com/.*/job/.*",
        r"icims\.com/.*/jobs/\d+",
        r"linkedin\.com/jobs/view/\d+",
        r"indeed\.com/viewjob\?jk=",
        r"glassdoor\.com/job-listing/.*",
        r"angel\.co/company/.*/jobs/.*",
        r"wellfound\.com/company/.*/jobs/.*",
        r"stackoverflow\.com/jobs/\d+",
        r"dice\.com/jobs/detail/.*",
        r"monster\.com/job-openings/.*",
        r"ziprecruiter\.com/jobs/.*",
        r"/job/\d+",
        r"/jobs/.+/\d+",
        r"/careers/.+/\d+",
    ],
    
    # Job listing page patterns
    "job_listing": [
        r"linkedin\.com/jobs/search",
        r"indeed\.com/jobs",
        r"glassdoor\.com/Jobs",
        r"angel\.co/jobs",
        r"wellfound\.com/jobs",
        r"stackoverflow\.com/jobs$",
        r"dice\.com/jobs",
        r"monster\.com/jobs",
        r"ziprecruiter\.com/jobs$",
        r"jobsearch",
        r"/jobs$",
        r"/jobs/$",
        r"/careers$",
        r"/careers/$",
        r"greenhouse\.io/.*$",  # Company greenhouse page
        r"lever\.co/.*$",       # Company lever page
    ],
    
    # Company careers pages
    "company_careers": [
        r"/careers/?$",
        r"/jobs/?$",
        r"/work-with-us/?$",
        r"/join-us/?$",
        r"/opportunities/?$",
        r"/positions/?$",
        r"/openings/?$",
    ]
}

# Platform detection patterns
PLATFORM_PATTERNS = {
    "linkedin": r"linkedin\.com",
    "indeed": r"indeed\.com",
    "glassdoor": r"glassdoor\.com",
    "greenhouse": r"greenhouse\.io",
    "lever": r"lever\.co",
    "ashby": r"ashbyhq\.com",
    "workday": r"workday\.com",
    "smartrecruiters": r"smartrecruiters\.com",
    "angel": r"angel\.co|wellfound\.com",
    "stackoverflow": r"stackoverflow\.com",
    "dice": r"dice\.com",
    "monster": r"monster\.com",
    "ziprecruiter": r"ziprecruiter\.com",
    "jobvite": r"jobvite\.com",
    "icims": r"icims\.com",
    "bamboohr": r"bamboohr\.com",
}

def classify_url_by_pattern(url: str) -> Dict[str, Any]:
    """Fast URL classification using regex patterns"""
    url_lower = url.lower()
    
    # Detect platform
    platform = "unknown"
    for platform_name, pattern in PLATFORM_PATTERNS.items():
        if re.search(pattern, url_lower):
            platform = platform_name
            break
    
    # Classify URL type
    for url_type, patterns in JOB_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return {
                    "type": url_type,
                    "platform": platform,
                    "confidence": 0.8,
                    "reason": f"Pattern match: {pattern}",
                    "method": "pattern"
                }
    
    return {
        "type": "not_relevant",
        "platform": platform,
        "confidence": 0.6,
        "reason": "No known patterns matched",
        "method": "pattern"
    }

def analyze_page_content(page: Page, url: str) -> Dict[str, Any]:
    """Analyze page content using Playwright"""
    try:
        # Get page title and meta description
        title = page.title().lower()
        
        # Job posting indicators
        job_indicators = [
            "job description", "responsibilities", "requirements", "qualifications", 
            "apply now", "job details", "position", "role", "salary", "benefits",
            "experience required", "skills needed"
        ]
        
        # Listing page indicators  
        listing_indicators = [
            "search results", "jobs found", "filter", "sort by", "page", "results",
            "showing", "matches", "browse", "explore opportunities"
        ]
        
        # Get page text content (first 2000 chars for performance)
        content = page.inner_text("body")[:2000].lower()
        
        # Count indicators
        job_score = sum(1 for indicator in job_indicators if indicator in title or indicator in content)
        listing_score = sum(1 for indicator in listing_indicators if indicator in title or indicator in content)
        
        # Check for specific selectors
        selectors_check = {
            "job_description": page.locator("[class*='job-description'], [class*='job-detail'], [id*='job-description']").count() > 0,
            "apply_button": page.locator("button:has-text('Apply'), a:has-text('Apply'), [class*='apply']").count() > 0,
            "job_listings": page.locator("[class*='job-item'], [class*='job-card'], [class*='job-result']").count() > 3,
            "pagination": page.locator("[class*='pagination'], [class*='pager'], a:has-text('Next')").count() > 0,
        }
        
        # Determine type based on analysis
        if job_score >= 3 or selectors_check["job_description"] or selectors_check["apply_button"]:
            return {
                "type": "direct_job",
                "confidence": 0.9,
                "reason": f"Content analysis: {job_score} job indicators found",
                "method": "content",
                "metadata": {
                    "job_score": job_score,
                    "has_apply_button": selectors_check["apply_button"],
                    "has_job_description": selectors_check["job_description"]
                }
            }
        elif listing_score >= 2 or selectors_check["job_listings"] or selectors_check["pagination"]:
            return {
                "type": "job_listing", 
                "confidence": 0.85,
                "reason": f"Content analysis: {listing_score} listing indicators found",
                "method": "content",
                "metadata": {
                    "listing_score": listing_score,
                    "job_count": selectors_check["job_listings"],
                    "has_pagination": selectors_check["pagination"]
                }
            }
        elif any(keyword in title for keyword in ["career", "jobs", "opportunities"]):
            return {
                "type": "company_careers",
                "confidence": 0.7,
                "reason": "Career-related title found",
                "method": "content"
            }
        else:
            return {
                "type": "not_relevant",
                "confidence": 0.8,
                "reason": "No job-related content indicators found",
                "method": "content"
            }
            
    except Exception as e:
        logging.error(f"Error analyzing page content: {str(e)}")
        return {
            "type": "not_relevant",
            "confidence": 0.3,
            "reason": f"Content analysis failed: {str(e)}",
            "method": "error"
        }

@tool("analyze_job_url", args_schema=AnalyzeUrlInput)
def analyze_job_url(url: str) -> Dict[str, Any]:
    """
    Analyze a URL to determine if it's a direct job posting, job listing page, company careers page, or not relevant.
    Uses both pattern matching and content analysis for accurate classification.
    """
    try:
        # Check cache first
        cached_result = get_cached_url_analysis(url)
        if cached_result:
            logging.info(f"Using cached analysis for URL: {url}")
            return cached_result
        # First, try pattern-based classification (fast)
        pattern_result = classify_url_by_pattern(url)
        
        # If pattern gives high confidence, return it
        if pattern_result["confidence"] >= 0.8:
            return {
                "url": url,
                "type": pattern_result["type"],
                "confidence": pattern_result["confidence"],
                "platform": pattern_result["platform"],
                "reason": pattern_result["reason"],
                "metadata": {"method": "pattern"}
            }
        
        # Otherwise, use content analysis (slower but more accurate)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Set user agent and timeout
                page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)"})
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                content_result = analyze_page_content(page, url)
                
                # Combine pattern and content results
                final_confidence = max(pattern_result["confidence"], content_result["confidence"])
                final_type = content_result["type"] if content_result["confidence"] > pattern_result["confidence"] else pattern_result["type"]
                
                result = {
                    "url": url,
                    "type": final_type,
                    "confidence": final_confidence,
                    "platform": pattern_result["platform"],
                    "reason": f"{pattern_result['reason']} + {content_result['reason']}",
                    "metadata": {
                        "pattern_result": pattern_result,
                        "content_result": content_result
                    }
                }
                
                # Cache the result
                cache_url_analysis(url, result)
                return result
                
            finally:
                browser.close()
                
    except Exception as e:
        logging.error(f"Error analyzing URL {url}: {str(e)}")
        return {
            "url": url,
            "type": "not_relevant",
            "confidence": 0.1,
            "platform": "unknown",
            "reason": f"Analysis failed: {str(e)}",
            "metadata": {"error": str(e)}
        }