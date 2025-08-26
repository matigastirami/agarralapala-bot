#!/usr/bin/env python3
"""
Test script for the new job discovery system.
This tests the complete pipeline from URL analysis to job validation.
"""

import logging
import sys
import os
from typing import List

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.common.tools.analyze_job_url import analyze_job_url
from agents.common.tools.extract_jobs_from_listing import extract_jobs_from_listing  
from agents.common.tools.validate_job_posting import validate_job_posting
from agents.common.tools.batch_process_urls import batch_process_urls
from agents.common.tools.job_discovery_monitor import get_monitor_stats, log_monitor_summary

def setup_logging():
    """Set up logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_job_discovery.log')
        ]
    )

def test_url_analysis():
    """Test URL analysis functionality"""
    print("\n=== Testing URL Analysis ===")
    
    test_urls = [
        "https://www.linkedin.com/jobs/view/12345",  # Direct job
        "https://www.linkedin.com/jobs/search",      # Job listing
        "https://jobs.lever.co/company/job-id",      # Direct job (Lever)
        "https://jobs.lever.co/company",             # Job listing (Lever)
        "https://example.com/careers",               # Company careers
        "https://example.com/about",                 # Not relevant
    ]
    
    for url in test_urls:
        try:
            result = analyze_job_url(url)
            print(f"URL: {url}")
            print(f"Type: {result['type']}, Platform: {result['platform']}, Confidence: {result['confidence']}")
            print(f"Reason: {result['reason']}")
            print("-" * 50)
        except Exception as e:
            print(f"Error analyzing {url}: {str(e)}")

def test_job_validation():
    """Test job validation functionality"""
    print("\n=== Testing Job Validation ===")
    
    # Test with a few real job URLs (these may or may not work depending on the sites)
    test_job_urls = [
        "https://jobs.lever.co/openai/engineering",  # Might be a real job
        "https://example.com/fake-job-404",          # Should fail
    ]
    
    for url in test_job_urls:
        try:
            result = validate_job_posting(url)
            print(f"URL: {url}")
            print(f"Valid: {result['is_valid']}, Confidence: {result['confidence']}")
            print(f"Title: {result['title']}, Company: {result['company']}")
            print(f"Status: {result['status']}, Reason: {result['reason']}")
            print("-" * 50)
        except Exception as e:
            print(f"Error validating {url}: {str(e)}")

def test_listing_extraction():
    """Test job listing extraction"""
    print("\n=== Testing Listing Extraction ===")
    
    # Test with job board search pages
    test_listing_urls = [
        "https://jobs.lever.co/openai",  # OpenAI careers page
        # Add more test URLs here - be careful not to overwhelm external services
    ]
    
    for url in test_listing_urls:
        try:
            print(f"Extracting jobs from: {url}")
            jobs = extract_jobs_from_listing(url, max_jobs=5, max_pages=1)  # Limit for testing
            print(f"Extracted {len(jobs)} jobs")
            
            for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                print(f"  Job {i+1}: {job['title']} at {job['company']} - {job['url']}")
            
            print("-" * 50)
        except Exception as e:
            print(f"Error extracting from {url}: {str(e)}")

def test_batch_processing():
    """Test batch processing functionality"""
    print("\n=== Testing Batch Processing ===")
    
    # Test URLs including direct jobs and listings
    test_urls = [
        "https://jobs.lever.co/openai",               # Should extract multiple jobs
        "https://www.glassdoor.com/Jobs/remote-developer-jobs-SRCH_IL.0,6_IS11047_KO7,16.htm",  # Job search
        "https://stackoverflow.com/jobs",            # Job board
    ]
    
    try:
        print(f"Processing {len(test_urls)} URLs with batch processor...")
        result = batch_process_urls(
            urls=test_urls,
            max_jobs_per_listing=10,  # Limit for testing
            max_workers=2,            # Limit concurrent processing
            validate_jobs=True
        )
        
        print(f"\n=== Batch Processing Results ===")
        print(f"Total URLs processed: {result['total_urls_processed']}")
        print(f"Direct jobs found: {result['direct_jobs_found']}")
        print(f"Listings processed: {result['listings_processed']}")
        print(f"Jobs extracted from listings: {result['jobs_extracted_from_listings']}")
        print(f"Validated jobs: {result['validated_jobs']}")
        print(f"Unique jobs found: {result.get('unique_jobs_found', 0)}")
        print(f"Processing time: {result['processing_time']}s")
        print(f"Errors: {result['errors']}")
        
        # Show sample jobs
        unique_jobs = result.get("unique_jobs", [])
        print(f"\n=== Sample Jobs Found ===")
        for i, job in enumerate(unique_jobs[:5]):  # Show first 5 jobs
            print(f"Job {i+1}: {job['title']} at {job['company']}")
            print(f"  URL: {job['url']}")
            print(f"  Platform: {job['platform']}, Confidence: {job.get('validation_confidence', 0)}")
            print(f"  Description: {job['description'][:100]}...")
            print()
        
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        import traceback
        traceback.print_exc()

def test_caching():
    """Test caching functionality"""
    print("\n=== Testing Caching ===")
    
    test_url = "https://jobs.lever.co/openai"
    
    # First call - should hit the actual service
    print("First analysis (should not use cache):")
    start_time = time.time()
    result1 = analyze_job_url(test_url)
    time1 = time.time() - start_time
    print(f"Result: {result1['type']}, Time: {time1:.2f}s")
    
    # Second call - should use cache
    print("Second analysis (should use cache):")
    start_time = time.time()
    result2 = analyze_job_url(test_url)
    time2 = time.time() - start_time
    print(f"Result: {result2['type']}, Time: {time2:.2f}s")
    
    print(f"Cache speedup: {time1/time2:.1f}x faster" if time2 > 0 else "Cache used")

def main():
    """Run all tests"""
    setup_logging()
    
    print("🚀 Starting Job Discovery System Tests")
    print("=" * 60)
    
    try:
        # Run individual component tests
        test_url_analysis()
        
        # Skip the more intensive tests by default to avoid overwhelming external services
        # Uncomment these lines to run full tests:
        
        # test_job_validation()
        # test_listing_extraction()  
        # test_batch_processing()
        # test_caching()
        
        print("\n=== Performance Statistics ===")
        log_monitor_summary()
        
        stats = get_monitor_stats()
        print(f"\nDetailed stats: {stats}")
        
        print("\n✅ Job Discovery System Tests Completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import time
    exit_code = main()
    sys.exit(exit_code)