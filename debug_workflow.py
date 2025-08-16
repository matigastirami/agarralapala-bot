#!/usr/bin/env python3
"""
Debug script for step-by-step workflow execution.
This helps identify exactly where the "Must write to at least one of []" error occurs.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def debug_workflow_step_by_step():
    """Debug the workflow step by step"""
    logger.info("🔍 Starting step-by-step workflow debug...")
    
    try:
        # Step 1: Import and create workflow
        logger.info("Step 1: Importing workflow modules...")
        from workflows.job_matching_workflow import create_job_matching_workflow, WorkflowState
        
        logger.info("Step 2: Creating workflow...")
        workflow = create_job_matching_workflow()
        logger.info("✅ Workflow created successfully")
        
        # Step 3: Create initial state
        logger.info("Step 3: Creating initial state...")
        initial_state: WorkflowState = {
            "job_postings": [],
            "enriched_jobs": [],
            "matches": [],
            "errors": [],
            "current_step": ""
        }
        logger.info(f"✅ Initial state created: {initial_state}")
        
        # Step 4: Test individual nodes
        logger.info("Step 4: Testing individual nodes...")
        
        # Test fetch_job_postings node
        logger.info("Testing fetch_job_postings node...")
        from workflows.job_matching_workflow import fetch_job_postings
        state_after_fetch = fetch_job_postings(initial_state)
        logger.info(f"✅ Fetch node completed. Job postings: {len(state_after_fetch['job_postings'])}")
        
        # Test enrich_job_postings_step node
        logger.info("Testing enrich_job_postings_step node...")
        from workflows.job_matching_workflow import enrich_job_postings_step
        state_after_enrich = enrich_job_postings_step(state_after_fetch)
        logger.info(f"✅ Enrich node completed. Enriched jobs: {len(state_after_enrich['enriched_jobs'])}")
        
        # Test match_candidates_step node
        logger.info("Testing match_candidates_step node...")
        from workflows.job_matching_workflow import match_candidates_step
        state_after_match = match_candidates_step(state_after_enrich)
        logger.info(f"✅ Match node completed. Matches: {len(state_after_match['matches'])}")
        
        # Step 5: Test workflow invocation
        logger.info("Step 5: Testing workflow invocation...")
        try:
            result = workflow.invoke(initial_state)
            logger.info(f"✅ Workflow invocation successful! Final state: {result}")
        except Exception as e:
            logger.error(f"❌ Workflow invocation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def debug_enrichment_tool_specifically():
    """Debug the enrichment tool specifically since that's where the error might be"""
    logger.info("🔍 Debugging enrichment tool specifically...")
    
    try:
        from agents.common.tools.enrich_job_postings import enrich_job_postings
        from common.database.repositories.job_posting import JobPostingsRepository
        
        # Test database connection
        logger.info("Testing database connection...")
        repo = JobPostingsRepository()
        jobs = repo.get_job_postings()
        logger.info(f"✅ Database connection successful. Found {len(jobs)} job postings")
        
        # Test enrichment tool with empty list
        logger.info("Testing enrichment tool with empty list...")
        result = enrich_job_postings.invoke({"job_ids": []})
        logger.info(f"✅ Enrichment tool with empty list: {result}")
        
        # Test enrichment tool with None
        logger.info("Testing enrichment tool with None...")
        try:
            result = enrich_job_postings.invoke({"job_ids": None})
            logger.info(f"✅ Enrichment tool with None: {result}")
        except Exception as e:
            logger.warning(f"⚠️  Enrichment tool with None failed (trying empty dict): {str(e)}")
            try:
                result = enrich_job_postings.invoke({})
                logger.info(f"✅ Enrichment tool with empty dict: {result}")
            except Exception as e2:
                logger.warning(f"⚠️  Enrichment tool with empty dict also failed: {str(e2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enrichment tool debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    logger.info("🚀 Starting Workflow Debug Session")
    logger.info("=" * 60)
    
    # Debug 1: Enrichment tool specifically
    if not debug_enrichment_tool_specifically():
        logger.error("Enrichment tool debug failed. Stopping here.")
        return False
    
    logger.info("-" * 40)
    
    # Debug 2: Step by step workflow
    if not debug_workflow_step_by_step():
        logger.error("Step-by-step workflow debug failed.")
        return False
    
    logger.info("=" * 60)
    logger.info("✅ All debug tests completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
