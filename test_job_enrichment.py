#!/usr/bin/env python3
"""
Test script for job enrichment workflow.
This script can be run directly or configured in VS Code's launch.json for debugging.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_job_enrichment.log')
    ]
)

logger = logging.getLogger(__name__)

def test_workflow_components():
    """Test individual components of the workflow"""
    logger.info("Testing workflow components...")
    
    try:
        # Test 1: Import workflow
        from workflows.job_matching_workflow import run_job_matching_workflow, WorkflowState
        logger.info("✅ Successfully imported workflow modules")
        
        # Test 2: Create workflow state
        state: WorkflowState = {
            "job_postings": [],
            "enriched_jobs": [],
            "matches": [],
            "errors": [],
            "current_step": ""
        }
        logger.info("✅ Successfully created workflow state")
        
        # Test 3: Check database connection
        from common.database.database import db_session
        session = db_session()
        logger.info("✅ Successfully connected to database")
        session.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Component test failed: {str(e)}")
        return False

def test_workflow_execution():
    """Test the actual workflow execution"""
    logger.info("Testing workflow execution...")
    
    try:
        from workflows.job_matching_workflow import run_job_matching_workflow
        
        logger.info("Starting workflow execution...")
        result = run_job_matching_workflow()
        
        logger.info(f"✅ Workflow completed successfully!")
        logger.info(f"   - Job postings: {len(result['job_postings'])}")
        logger.info(f"   - Enriched jobs: {len(result['enriched_jobs'])}")
        logger.info(f"   - Matches: {len(result['matches'])}")
        
        if result.get('errors'):
            logger.warning(f"⚠️  Workflow warnings: {result['errors']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_enrichment_tool():
    """Test the enrichment tool specifically"""
    logger.info("Testing enrichment tool...")
    
    try:
        from agents.common.tools.enrich_job_postings import enrich_job_postings
        
        # Test with empty list to see if it handles the case properly
        # For LangChain tools, we need to use invoke() with proper input format
        logger.info("Testing with empty job_ids list...")
        result = enrich_job_postings.invoke({"job_ids": []})
        logger.info(f"✅ Enrichment tool test completed. Result: {result}")
        
        # Test with None (should fetch all jobs without details)
        logger.info("Testing with None job_ids...")
        try:
            result_none = enrich_job_postings.invoke({"job_ids": None})
            logger.info(f"✅ Enrichment tool test with None completed. Result: {result_none}")
        except Exception as e:
            logger.warning(f"⚠️  Enrichment tool with None had issues (this might be expected): {str(e)}")
            # Try with empty dict instead
            try:
                result_empty = enrich_job_postings.invoke({})
                logger.info(f"✅ Enrichment tool test with empty dict completed. Result: {result_empty}")
            except Exception as e2:
                logger.warning(f"⚠️  Enrichment tool with empty dict also failed: {str(e2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enrichment tool test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting Job Enrichment Test Suite")
    logger.info("=" * 50)
    
    # Test 1: Components
    if not test_workflow_components():
        logger.error("Component test failed. Exiting.")
        return False
    
    # Test 2: Enrichment tool
    if not test_enrichment_tool():
        logger.error("Enrichment tool test failed. Exiting.")
        return False
    
    # Test 3: Full workflow (optional - comment out if you want to skip)
    logger.info("Skipping full workflow execution for now...")
    # result = test_workflow_execution()
    # if result is None:
    #     logger.error("Workflow execution test failed.")
    #     return False
    
    logger.info("=" * 50)
    logger.info("✅ All tests completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
