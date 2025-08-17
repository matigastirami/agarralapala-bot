# Job Enrichment Improvements: Expired Job Detection

## Overview

The job enrichment process has been significantly improved to detect and handle expired, filled, or unavailable job postings. This prevents the system from processing and storing jobs that are no longer active.

## Problem Solved

Previously, the system would attempt to scrape all job postings regardless of their availability status, leading to:
- Processing of expired/filled jobs
- Storage of invalid job data
- Wasted processing time on unavailable positions
- Poor user experience with outdated job information

## Solution Implemented

### 1. Job Status Tracking

Added a new `status` field to the `JobPosting` model with the following values:
- `active` - Job is available and can be applied to
- `expired` - Job has been filled, expired, or is no longer available
- `error` - Error occurred during processing
- `filled` - Position has been filled (alternative to expired)

### 2. Platform-Specific Detection

The system now detects expired jobs across different ATS platforms:

#### Ashby (jobs.ashbyhq.com)
- Detects "Job not found" messages
- Identifies "This position has been filled" notices

#### Startup.jobs
- Detects "This job is no longer available" messages
- Identifies filled positions

#### Lever (jobs.lever.co)
- Detects filled positions and unavailable jobs
- Handles 404 errors and "not found" pages

#### Greenhouse (boards.greenhouse.io)
- Detects filled positions and unavailable jobs
- Handles 404 errors and "not found" pages

### 3. Generic Pattern Detection

For platforms not specifically handled, the system uses generic patterns:
- "This position has been filled"
- "This job is no longer available"
- "Position has been filled"
- "Job has been filled"
- "This opportunity is no longer available"
- "Position has been closed"
- "Job has been closed"
- "404", "not found", "page not found"
- "Job not found", "position not found"

### 4. Content Validation

The system also validates that pages have sufficient content:
- Pages with less than 100 characters are flagged as potentially expired
- This catches generic error pages or empty responses

## Implementation Details

### Database Changes

```sql
-- New status field added to job_postings table
ALTER TABLE job_postings ADD COLUMN status VARCHAR(32) DEFAULT 'active' NOT NULL;
```

### New Repository Methods

```python
# Get only active job postings
def get_active_job_postings(self):
    return self.session.query(JobPosting).filter(JobPosting.status == 'active').all()

# Get jobs by status
def get_job_postings_by_status(self, status: str):
    return self.session.query(JobPosting).filter(JobPosting.status == status).all()

# Update job status
def update_job_status(self, job_id: int, status: str):
    # Updates only the status field
```

### Enhanced Enrichment Process

1. **Job Availability Check**: Before scraping, check if the job is still available
2. **Status Update**: Mark expired jobs in the database
3. **Skip Processing**: Skip detailed scraping for expired jobs
4. **Error Handling**: Mark jobs with processing errors

## Usage Examples

### Testing Expired Job Detection

```python
from agents.common.tools.enrich_job_postings import check_job_availability

# Test with expired Ashby job
url = "https://jobs.ashbyhq.com/Deel/bb349fda-7b81-48c2-aabe-c1990999d648"
status = check_job_availability(page, url)
# Returns: {'status': 'expired', 'reason': 'Job not found (Ashby)'}
```

### Getting Active Jobs Only

```python
from common.database.repositories.job_posting import JobPostingsRepository

repo = JobPostingsRepository()
active_jobs = repo.get_active_job_postings()
# Only returns jobs with status = 'active'
```

### Manual Status Update

```python
repo = JobPostingsRepository()
repo.update_job_status(job_id=123, status='expired')
```

## Benefits

1. **Improved Data Quality**: Only active jobs are processed and stored
2. **Better Performance**: Reduced processing time by skipping expired jobs
3. **Enhanced User Experience**: Users only see available job opportunities
4. **Platform Flexibility**: Handles multiple ATS platforms with specific detection logic
5. **Future-Proof**: Generic patterns catch new platforms automatically

## Testing

Run the improved test suite:

```bash
python test_job_enrichment_improved.py
```

This will test:
- Expired job detection across different platforms
- Platform-specific content extraction
- Database integration with new status field
- Overall enrichment tool functionality

## Migration

To apply the database changes:

```bash
# Create migration
alembic revision --autogenerate -m "add_job_status_field"

# Apply migration
alembic upgrade head
```

## Monitoring

Monitor the enrichment process logs for:
- Expired job detection messages
- Status updates in the database
- Processing efficiency improvements

Example log output:
```
INFO - Enriching job posting 123: Senior Software Engineer
WARNING - Job 123 is expired/filled: Job not found (Ashby)
INFO - Enriching job posting 124: Frontend Developer
INFO - Successfully enriched job 124
```
