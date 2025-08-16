# Upsert Implementation for Job Postings and Matches

## Overview

This document describes the implementation of upsert (update or insert) functionality for job postings and matches to prevent duplication in the database when the cron jobs run repeatedly.

## Problem Solved

Previously, the system was creating duplicate records every time the cron jobs ran because:
1. No unique constraints existed in the database
2. Simple insert operations were used instead of upsert logic
3. No deduplication logic was implemented

## Solution Implemented

### 1. Database Schema Changes

#### Unique Constraints Added
- **Job Postings**: Unique constraint on `job_link` field
- **Matches**: Composite unique constraint on `candidate_id + job_posting_id`

#### Migration File
- Created: `common/database/migrations/versions/854a9eb89f00_add_unique_constraints_for_upsert.py`
- Applied successfully to prevent duplicate entries at the database level

### 2. Model Updates

#### JobPosting Model (`common/database/models/job_posting.py`)
```python
job_link = Column(String(length=512), nullable=False, unique=True)
```

#### Match Model (`common/database/models/match.py`)
```python
__table_args__ = (
    UniqueConstraint('candidate_id', 'job_posting_id', name='uq_matches_candidate_job'),
)
```

### 3. Repository Layer Updates

#### JobPostingsRepository (`common/database/repositories/job_posting.py`)

**New Methods:**
- `upsert_job_posting(job_data: dict)` - Single job upsert
- `get_by_job_link(job_link: str)` - Get job by link
- `exists_by_job_link(job_link: str) -> bool` - Check existence

**Updated Methods:**
- `save_job_postings(jobs_list: list[dict])` - Now uses upsert logic
  - Checks for existing jobs by `job_link`
  - Updates existing records or inserts new ones
  - Commits each job individually to avoid transaction conflicts

#### MatchesRepository (`common/database/repositories/matches.py`)

**New Methods:**
- `upsert_match(match_data: dict)` - Single match upsert
- `get_match_by_candidate_and_job(candidate_id: int, job_posting_id: int)` - Get specific match
- `exists_by_candidate_and_job(candidate_id: int, job_posting_id: int) -> bool` - Check existence

**Updated Methods:**
- `save_matches(matches_list: list[dict])` - Now uses upsert logic
  - Checks for existing matches by `candidate_id + job_posting_id`
  - Updates existing records or inserts new ones
  - Commits each match individually to avoid transaction conflicts

### 4. Tool Layer Updates

#### save_job_postings Tool (`agents/common/tools/save_job_postings.py`)
- Updated to use upsert functionality
- Added proper error handling
- Handles None/empty input gracefully
- Returns informative success/error messages

#### save_matches Tool (`agents/common/tools/save_matches.py`)
- Updated to use upsert functionality
- Added proper error handling
- Handles None/empty input gracefully
- Returns informative success/error messages

## Key Features

### 1. Upsert Logic
- **Job Postings**: Uses `job_link` as unique identifier
- **Matches**: Uses `candidate_id + job_posting_id` as composite unique identifier
- Automatically detects existing records and updates them
- Inserts new records when they don't exist

### 2. Transaction Safety
- Individual commits for each record to avoid transaction conflicts
- Proper rollback on errors
- Detailed error reporting and logging

### 3. Performance Optimizations
- Efficient database queries using unique constraints
- Minimal database round trips
- Proper session management

### 4. Error Handling
- Graceful handling of duplicate key violations
- Comprehensive error messages
- Rollback on failures to maintain data consistency

## Testing

### Test Files Created
1. `test_upsert_functionality.py` - Comprehensive upsert testing
2. `test_workflow_upsert.py` - Workflow tool integration testing

### Test Coverage
- ✅ Individual upsert operations
- ✅ Bulk upsert operations
- ✅ Duplicate handling
- ✅ Error scenarios
- ✅ Empty/None input handling
- ✅ Workflow tool integration

### Test Results
```
📊 Test Results: 3/3 tests passed (Core functionality)
📊 Test Results: 2/2 tests passed (Workflow integration)
🎉 All tests passed! Upsert functionality is working correctly.
```

## Usage Examples

### Single Job Posting Upsert
```python
repo = JobPostingsRepository()
job_data = {
    'job_title': 'Software Engineer',
    'company_name': 'Tech Corp',
    'job_link': 'https://example.com/job1',
    'quick_description': 'Engineering role'
}
result = repo.upsert_job_posting(job_data)
```

### Bulk Job Postings Upsert
```python
repo = JobPostingsRepository()
jobs_list = [
    {'job_title': 'Dev 1', 'company_name': 'Corp', 'job_link': 'https://example.com/job1'},
    {'job_title': 'Dev 2', 'company_name': 'Corp', 'job_link': 'https://example.com/job2'}
]
repo.save_job_postings(jobs_list)
```

### Single Match Upsert
```python
repo = MatchesRepository()
match_data = {
    'candidate_id': 1,
    'job_posting_id': 1,
    'match_score': 0.85,
    'strengths': 'Good skills'
}
result = repo.upsert_match(match_data)
```

### Bulk Matches Upsert
```python
repo = MatchesRepository()
matches_list = [
    {'candidate_id': 1, 'job_posting_id': 1, 'match_score': 0.85},
    {'candidate_id': 2, 'job_posting_id': 1, 'match_score': 0.90}
]
repo.save_matches(matches_list)
```

## Benefits

1. **No More Duplicates**: Prevents duplicate job postings and matches
2. **Data Consistency**: Maintains data integrity across multiple cron runs
3. **Performance**: Efficient database operations with proper indexing
4. **Reliability**: Robust error handling and transaction management
5. **Scalability**: Handles both individual and bulk operations efficiently

## Migration Notes

- The unique constraints were added via Alembic migration
- Existing data should be cleaned up before applying constraints (if duplicates exist)
- The migration is reversible and can be rolled back if needed

## Future Enhancements

1. **Batch Processing**: Implement true batch upserts for better performance
2. **Conflict Resolution**: Add configurable conflict resolution strategies
3. **Audit Trail**: Track when records are updated vs inserted
4. **Metrics**: Add monitoring for upsert operations

