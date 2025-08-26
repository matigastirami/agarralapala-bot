from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .analyze_job_url import analyze_job_url
from .extract_jobs_from_listing import extract_jobs_from_listing
from .validate_job_posting import validate_job_posting
from .job_discovery_monitor import monitor_operation, job_monitor, PLAYWRIGHT_RATE_LIMITER
from .job_discovery_cache import (
    get_cached_url_analysis, cache_url_analysis,
    get_cached_job_validation, cache_job_validation,
    get_cached_listing_extraction, cache_listing_extraction
)

class BatchProcessInput(BaseModel):
    urls: List[str] = Field(description="List of URLs to process")
    max_jobs_per_listing: int = Field(description="Maximum jobs to extract per listing page", default=30)
    max_workers: int = Field(description="Maximum concurrent workers", default=3)
    validate_jobs: bool = Field(description="Whether to validate extracted job postings", default=True)

class BatchProcessResult(BaseModel):
    total_urls_processed: int
    direct_jobs_found: int
    listings_processed: int
    jobs_extracted_from_listings: int
    validated_jobs: int
    invalid_jobs: int
    errors: int
    processing_time: float
    results: List[Dict[str, Any]]

@monitor_operation("process_single_url")
def process_single_url(url: str, max_jobs_per_listing: int = 30, validate: bool = True) -> Dict[str, Any]:
    """Process a single URL through the complete pipeline"""
    result = {
        "original_url": url,
        "url_type": "unknown",
        "jobs": [],
        "errors": [],
        "processing_time": 0
    }
    
    start_time = time.time()
    
    try:
        # Step 1: Analyze URL type (with caching)
        cached_analysis = get_cached_url_analysis(url)
        if cached_analysis:
            analysis = cached_analysis
            logging.info(f"Using cached analysis for {url}")
        else:
            analysis = analyze_job_url(url)
            cache_url_analysis(url, analysis)
        
        result["url_type"] = analysis["type"]
        result["platform"] = analysis.get("platform", "unknown")
        result["confidence"] = analysis.get("confidence", 0)
        
        # Step 2: Process based on URL type
        if analysis["type"] == "direct_job":
            # This is already a job posting, validate if requested
            if validate:
                cached_validation = get_cached_job_validation(url)
                if cached_validation:
                    validation = cached_validation
                    logging.info(f"Using cached validation for {url}")
                else:
                    validation = validate_job_posting(url)
                    cache_job_validation(url, validation)
                
                if validation["is_valid"]:
                    result["jobs"].append({
                        "url": url,
                        "title": validation["title"],
                        "company": validation["company"],
                        "location": validation["location"],
                        "description": validation["description"][:200],
                        "platform": result["platform"],
                        "validation_confidence": validation["confidence"],
                        "source": "direct"
                    })
                else:
                    result["errors"].append(f"Direct job validation failed: {validation['reason']}")
            else:
                # Add without validation
                result["jobs"].append({
                    "url": url,
                    "title": "",
                    "company": "",
                    "location": "",
                    "description": "",
                    "platform": result["platform"],
                    "validation_confidence": 1.0,
                    "source": "direct"
                })
        
        elif analysis["type"] == "job_listing":
            # Extract jobs from listing page (with caching)
            try:
                cached_extraction = get_cached_listing_extraction(url)
                if cached_extraction:
                    extracted_jobs = cached_extraction
                    logging.info(f"Using cached extraction for listing {url}")
                else:
                    extracted_jobs = extract_jobs_from_listing(
                        url=url, 
                        max_jobs=max_jobs_per_listing,
                        max_pages=2  # Limit pages for batch processing
                    )
                    cache_listing_extraction(url, extracted_jobs)
                
                logging.info(f"Extracted {len(extracted_jobs)} jobs from listing {url}")
                
                # Validate extracted jobs if requested
                if validate and extracted_jobs:
                    validated_jobs = []
                    for job in extracted_jobs:
                        try:
                            job_url = job["url"]
                            
                            cached_validation = get_cached_job_validation(job_url)
                            if cached_validation:
                                validation = cached_validation
                            else:
                                validation = validate_job_posting(job_url)
                                cache_job_validation(job_url, validation)
                            
                            if validation["is_valid"]:
                                validated_jobs.append({
                                    "url": job_url,
                                    "title": validation["title"] or job["title"],
                                    "company": validation["company"] or job["company"],
                                    "location": validation["location"] or job["location"],
                                    "description": validation["description"][:200],
                                    "platform": job["platform"],
                                    "validation_confidence": validation["confidence"],
                                    "source": "extracted"
                                })
                        except Exception as e:
                            result["errors"].append(f"Error validating extracted job {job.get('url', 'unknown')}: {str(e)}")
                    
                    result["jobs"] = validated_jobs
                else:
                    # Add extracted jobs without validation
                    result["jobs"] = [{
                        "url": job["url"],
                        "title": job["title"],
                        "company": job["company"],
                        "location": job["location"],
                        "description": job.get("snippet", "")[:200],
                        "platform": job["platform"],
                        "validation_confidence": 0.7,  # Default confidence
                        "source": "extracted"
                    } for job in extracted_jobs]
                    
            except Exception as e:
                result["errors"].append(f"Error extracting from listing: {str(e)}")
        
        elif analysis["type"] == "company_careers":
            # Try to extract jobs from company career page
            try:
                extracted_jobs = extract_jobs_from_listing(
                    url=url,
                    max_jobs=max_jobs_per_listing,
                    max_pages=1  # Only first page for company careers
                )
                
                if extracted_jobs:
                    logging.info(f"Extracted {len(extracted_jobs)} jobs from company careers {url}")
                    
                    # Add extracted jobs (optionally validate)
                    if validate:
                        validated_jobs = []
                        for job in extracted_jobs[:10]:  # Limit validation for company pages
                            try:
                                validation = validate_job_posting(job["url"])
                                if validation["is_valid"]:
                                    validated_jobs.append({
                                        "url": job["url"],
                                        "title": validation["title"] or job["title"],
                                        "company": validation["company"] or job["company"],
                                        "location": validation["location"] or job["location"],
                                        "description": validation["description"][:200],
                                        "platform": job["platform"],
                                        "validation_confidence": validation["confidence"],
                                        "source": "company_careers"
                                    })
                            except:
                                continue
                        result["jobs"] = validated_jobs
                    else:
                        result["jobs"] = [{
                            "url": job["url"],
                            "title": job["title"],
                            "company": job["company"],
                            "location": job["location"],
                            "description": job.get("snippet", "")[:200],
                            "platform": job["platform"],
                            "validation_confidence": 0.6,
                            "source": "company_careers"
                        } for job in extracted_jobs]
                        
            except Exception as e:
                result["errors"].append(f"Error processing company careers page: {str(e)}")
        
        else:
            # Not relevant - skip
            result["errors"].append(f"URL classified as not relevant: {analysis.get('reason', '')}")
    
    except Exception as e:
        result["errors"].append(f"Error processing URL: {str(e)}")
        logging.error(f"Error processing {url}: {str(e)}")
    
    result["processing_time"] = time.time() - start_time
    return result

@tool("batch_process_urls", args_schema=BatchProcessInput)
@monitor_operation("batch_process_urls")
def batch_process_urls(
    urls: List[str], 
    max_jobs_per_listing: int = 30,
    max_workers: int = 3,
    validate_jobs: bool = True
) -> Dict[str, Any]:
    """
    Process multiple URLs efficiently through the complete job discovery pipeline.
    Analyzes URL types, extracts jobs from listings, and optionally validates job postings.
    """
    
    if not urls:
        return {
            "total_urls_processed": 0,
            "direct_jobs_found": 0,
            "listings_processed": 0, 
            "jobs_extracted_from_listings": 0,
            "validated_jobs": 0,
            "invalid_jobs": 0,
            "errors": 0,
            "processing_time": 0.0,
            "results": []
        }
    
    start_time = time.time()
    all_results = []
    
    logging.info(f"Starting batch processing of {len(urls)} URLs with {max_workers} workers")
    
    try:
        # Process URLs concurrently with thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_url = {
                executor.submit(process_single_url, url, max_jobs_per_listing, validate_jobs): url 
                for url in urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=120)  # 2 minute timeout per URL
                    all_results.append(result)
                    logging.info(f"Completed processing {url}: found {len(result['jobs'])} jobs")
                except Exception as e:
                    logging.error(f"Error processing {url}: {str(e)}")
                    all_results.append({
                        "original_url": url,
                        "url_type": "error",
                        "jobs": [],
                        "errors": [f"Processing failed: {str(e)}"],
                        "processing_time": 0
                    })
    
    except Exception as e:
        logging.error(f"Error in batch processing: {str(e)}")
        return {
            "total_urls_processed": 0,
            "direct_jobs_found": 0,
            "listings_processed": 0,
            "jobs_extracted_from_listings": 0,
            "validated_jobs": 0,
            "invalid_jobs": 0,
            "errors": 1,
            "processing_time": time.time() - start_time,
            "results": [],
            "error": str(e)
        }
    
    # Compile statistics
    total_jobs = []
    direct_jobs_count = 0
    listings_processed_count = 0
    jobs_from_listings_count = 0
    validated_jobs_count = 0
    invalid_jobs_count = 0
    total_errors = 0
    
    for result in all_results:
        total_jobs.extend(result["jobs"])
        total_errors += len(result["errors"])
        
        if result["url_type"] == "direct_job":
            direct_jobs_count += len(result["jobs"])
        elif result["url_type"] == "job_listing":
            listings_processed_count += 1
            jobs_from_listings_count += len(result["jobs"])
        elif result["url_type"] == "company_careers":
            listings_processed_count += 1
            jobs_from_listings_count += len(result["jobs"])
        
        # Count validated jobs
        for job in result["jobs"]:
            if job.get("validation_confidence", 0) > 0.6:
                validated_jobs_count += 1
            else:
                invalid_jobs_count += 1
    
    # Remove duplicate jobs based on URL
    unique_jobs = []
    seen_urls = set()
    for job in total_jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)
    
    processing_time = time.time() - start_time
    
    result_summary = {
        "total_urls_processed": len(all_results),
        "direct_jobs_found": direct_jobs_count,
        "listings_processed": listings_processed_count,
        "jobs_extracted_from_listings": jobs_from_listings_count,
        "validated_jobs": validated_jobs_count,
        "invalid_jobs": invalid_jobs_count,
        "unique_jobs_found": len(unique_jobs),
        "total_jobs_before_dedup": len(total_jobs),
        "errors": total_errors,
        "processing_time": round(processing_time, 2),
        "results": all_results,
        "unique_jobs": unique_jobs
    }
    
    logging.info(f"Batch processing completed: {len(unique_jobs)} unique jobs found from {len(urls)} URLs in {processing_time:.1f}s")
    
    return result_summary