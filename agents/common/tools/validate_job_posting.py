from langchain_core.tools import tool
from playwright.sync_api import sync_playwright, Page
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import re
import logging
from urllib.parse import urlparse

class ValidateJobInput(BaseModel):
    url: str = Field(description="The job posting URL to validate")

class JobValidationResult(BaseModel):
    url: str
    is_valid: bool
    confidence: float
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    requirements: str = ""
    status: str  # "active", "expired", "filled", "error"
    reason: str
    metadata: Dict[str, Any] = {}

def extract_job_metadata(page: Page, url: str) -> Dict[str, Any]:
    """Extract job metadata from the page"""
    metadata = {
        "title": "",
        "company": "",
        "location": "",
        "description": "",
        "requirements": "",
        "salary": "",
        "job_type": "",
        "seniority": ""
    }
    
    try:
        # Title extraction - try multiple selectors
        title_selectors = [
            "h1",
            "[data-test='job-title']",
            ".job-title",
            "[class*='job-title']", 
            "[class*='position-title']",
            ".posting-headline h2",
            ".job-view-job-title"
        ]
        
        for selector in title_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                metadata["title"] = elements.first.inner_text().strip()
                if metadata["title"]:
                    break
        
        # Company extraction
        company_selectors = [
            "[data-test='company-name']",
            ".company-name",
            "[class*='company']",
            "[class*='employer']",
            ".posting-company h2",
            ".job-view-job-company"
        ]
        
        for selector in company_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                metadata["company"] = elements.first.inner_text().strip()
                if metadata["company"]:
                    break
        
        # Location extraction
        location_selectors = [
            "[data-test='job-location']",
            ".location",
            "[class*='location']",
            "[class*='loc']",
            ".posting-categories .location"
        ]
        
        for selector in location_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                metadata["location"] = elements.first.inner_text().strip()
                if metadata["location"]:
                    break
        
        # Description extraction
        desc_selectors = [
            "[data-test='job-description']",
            ".job-description",
            "[class*='description']",
            ".posting-content",
            ".job-view-job-description",
            "[class*='job-details']"
        ]
        
        for selector in desc_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                desc_text = elements.first.inner_text().strip()
                if len(desc_text) > 100:  # Only consider substantial descriptions
                    metadata["description"] = desc_text[:1000]  # Limit to 1000 chars
                    break
        
        # Requirements extraction - look for sections containing requirements
        req_keywords = ["requirements", "qualifications", "must have", "skills", "experience"]
        content = page.inner_text("body").lower()
        
        for keyword in req_keywords:
            if keyword in content:
                # Try to find the requirements section
                req_selectors = [
                    f"*:has-text('{keyword}') + *",
                    f"h2:has-text('{keyword}') + *",
                    f"h3:has-text('{keyword}') + *",
                    f"*:has-text('{keyword}') ~ ul",
                    f"*:has-text('{keyword}') ~ div"
                ]
                
                for selector in req_selectors:
                    try:
                        elements = page.locator(selector)
                        if elements.count() > 0:
                            req_text = elements.first.inner_text().strip()
                            if len(req_text) > 50:
                                metadata["requirements"] = req_text[:500]
                                break
                    except:
                        continue
                
                if metadata["requirements"]:
                    break
        
        # Salary extraction
        salary_patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'\$[\d,]+k?\s*-\s*\$?[\d,]+k?',
            r'[\d,]+k?\s*-\s*[\d,]+k?\s*(?:USD|EUR|GBP)',
            r'salary.*?[\d,]+',
            r'compensation.*?[\d,]+'
        ]
        
        page_text = page.inner_text("body")
        for pattern in salary_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                metadata["salary"] = matches[0].strip()
                break
        
        return metadata
        
    except Exception as e:
        logging.warning(f"Error extracting metadata: {str(e)}")
        return metadata

def check_job_status(page: Page, url: str) -> Dict[str, str]:
    """Check if job is still active/available"""
    try:
        page_text = page.inner_text("body").lower()
        page_title = page.title().lower()
        
        # Expired/filled indicators
        expired_indicators = [
            "no longer accepting applications",
            "position has been filled",
            "job is no longer available", 
            "position closed",
            "expired",
            "filled",
            "not found",
            "404",
            "page not found",
            "removed",
            "deleted",
            "unavailable"
        ]
        
        # Check for expired indicators
        for indicator in expired_indicators:
            if indicator in page_text or indicator in page_title:
                return {"status": "expired", "reason": f"Found indicator: {indicator}"}
        
        # Check for active indicators
        active_indicators = [
            "apply now",
            "submit application", 
            "apply for this position",
            "apply online",
            "join our team",
            "we are hiring",
            "apply today"
        ]
        
        for indicator in active_indicators:
            if indicator in page_text:
                return {"status": "active", "reason": f"Found active indicator: {indicator}"}
        
        # Check for apply buttons
        apply_selectors = [
            "button:has-text('Apply')",
            "a:has-text('Apply')",
            "[class*='apply']",
            "[data-test*='apply']",
            "input[value*='Apply']"
        ]
        
        for selector in apply_selectors:
            if page.locator(selector).count() > 0:
                return {"status": "active", "reason": "Found apply button"}
        
        # Default to active if no clear indicators
        return {"status": "active", "reason": "No expiration indicators found"}
        
    except Exception as e:
        return {"status": "error", "reason": f"Status check failed: {str(e)}"}

def validate_job_content(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that extracted content looks like a real job posting"""
    validation_score = 0
    reasons = []
    
    # Check if we have a title
    if metadata["title"]:
        validation_score += 25
        reasons.append("Has job title")
        
        # Check if title contains job-related keywords
        job_keywords = ["developer", "engineer", "manager", "analyst", "designer", "specialist", "coordinator", "director", "lead", "senior", "junior", "intern"]
        if any(keyword in metadata["title"].lower() for keyword in job_keywords):
            validation_score += 10
            reasons.append("Title contains job keywords")
    
    # Check if we have a company
    if metadata["company"]:
        validation_score += 20
        reasons.append("Has company name")
    
    # Check if we have a substantial description
    if metadata["description"] and len(metadata["description"]) > 200:
        validation_score += 25
        reasons.append("Has substantial job description")
        
        # Check for job-specific content in description
        job_content_keywords = [
            "responsibilities", "duties", "requirements", "qualifications", 
            "experience", "skills", "benefits", "salary", "team", "role"
        ]
        
        desc_lower = metadata["description"].lower()
        matching_keywords = sum(1 for keyword in job_content_keywords if keyword in desc_lower)
        
        if matching_keywords >= 3:
            validation_score += 15
            reasons.append(f"Description contains {matching_keywords} job-related keywords")
    
    # Check if we have requirements
    if metadata["requirements"]:
        validation_score += 10
        reasons.append("Has requirements section")
    
    # Check for location
    if metadata["location"]:
        validation_score += 5
        reasons.append("Has location")
    
    # Check for salary information
    if metadata["salary"]:
        validation_score += 5
        reasons.append("Has salary information")
    
    is_valid = validation_score >= 60  # Require at least 60% score
    confidence = min(validation_score / 100.0, 1.0)
    
    return {
        "is_valid": is_valid,
        "confidence": confidence,
        "score": validation_score,
        "reasons": reasons
    }

@tool("validate_job_posting", args_schema=ValidateJobInput)
def validate_job_posting(url: str) -> Dict[str, Any]:
    """
    Validate that a URL points to an active, real job posting.
    Extracts job metadata and checks if the posting is still available.
    """
    try:
        logging.info(f"Validating job posting: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                # Navigate to job posting
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Check job status
                status_info = check_job_status(page, url)
                
                # Extract metadata
                metadata = extract_job_metadata(page, url)
                
                # Validate content
                validation_result = validate_job_content(metadata)
                
                # Combine results
                result = {
                    "url": url,
                    "is_valid": validation_result["is_valid"] and status_info["status"] == "active",
                    "confidence": validation_result["confidence"] * (0.9 if status_info["status"] == "active" else 0.3),
                    "title": metadata["title"],
                    "company": metadata["company"],
                    "location": metadata["location"], 
                    "description": metadata["description"][:500],  # Truncate for response
                    "requirements": metadata["requirements"][:300],  # Truncate for response
                    "status": status_info["status"],
                    "reason": f"Validation: {', '.join(validation_result['reasons'])}. Status: {status_info['reason']}",
                    "metadata": {
                        "validation_score": validation_result["score"],
                        "salary": metadata.get("salary", ""),
                        "job_type": metadata.get("job_type", ""),
                        "full_description_length": len(metadata.get("description", "")),
                        "requirements_length": len(metadata.get("requirements", ""))
                    }
                }
                
                return result
                
            finally:
                browser.close()
                
    except Exception as e:
        logging.error(f"Error validating job posting {url}: {str(e)}")
        return {
            "url": url,
            "is_valid": False,
            "confidence": 0.0,
            "title": "",
            "company": "",
            "location": "",
            "description": "",
            "requirements": "",
            "status": "error",
            "reason": f"Validation failed: {str(e)}",
            "metadata": {"error": str(e)}
        }