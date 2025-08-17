from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from agents.job_seeker.agent import JobSeekerAgent
from agents.candidate_matcher.agent import CandidateMatcherAgent
from agents.job_enricher.agent import JobEnricherAgent
import logging

# Define the state schema as a TypedDict for proper LangGraph compatibility
class WorkflowState(TypedDict):
    job_postings: List[Dict[str, Any]]
    enriched_jobs: List[Dict[str, Any]]
    matches: List[Dict[str, Any]]
    errors: List[str]
    current_step: str

# Node functions for the workflow - these must return dictionaries
def fetch_job_postings(state: WorkflowState) -> WorkflowState:
    """Step 1: Fetch job postings using the job seeker agent"""
    try:
        logging.info("Starting job posting fetch step")
        
        job_seeker = JobSeekerAgent()
        result = job_seeker.exec()
        
        # Parse the result to get job postings
        # This depends on how your job_seeker agent returns data
        if isinstance(result, dict):
            job_postings = result.get('job_postings', [])
        elif isinstance(result, list):
            job_postings = result
        else:
            job_postings = []
            
        logging.info(f"Fetched {len(job_postings)} job postings")
        
        # If no job postings found, log a warning but continue
        if not job_postings:
            logging.warning("No job postings found in this run")
        
        return {
            **state,
            "job_postings": job_postings,
            "current_step": "fetching_jobs"
        }
        
    except Exception as e:
        logging.error(f"Error in fetch_job_postings: {str(e)}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"Fetch error: {str(e)}"],
            "current_step": "fetching_jobs"
        }

def enrich_job_postings_step(state: WorkflowState) -> WorkflowState:
    """Step 2: Enrich job postings with detailed descriptions using the job enricher agent"""
    try:
        logging.info("Starting job enrichment step")
        
        job_postings = state.get("job_postings", [])
        if not job_postings:
            logging.warning("No job postings to enrich - skipping enrichment step")
            return {
                **state,
                "enriched_jobs": [],
                "current_step": "enriching_jobs"
            }
        
        # Use the job enricher agent
        job_enricher = JobEnricherAgent()
        result = job_enricher.exec()
        
        # Parse the result to get enriched jobs
        if isinstance(result, dict):
            enriched_results = result.get('enriched_jobs', [])
        elif isinstance(result, list):
            enriched_results = result
        else:
            enriched_results = []
            
        logging.info(f"Enriched {len(enriched_results)} job postings")
        
        return {
            **state,
            "enriched_jobs": enriched_results,
            "current_step": "enriching_jobs"
        }
        
    except Exception as e:
        logging.error(f"Error in enrich_job_postings_step: {str(e)}")
        return {
            **state,
            "enriched_jobs": [],
            "errors": state.get("errors", []) + [f"Enrichment error: {str(e)}"],
            "current_step": "enriching_jobs"
        }

def match_candidates_step(state: WorkflowState) -> WorkflowState:
    """Step 3: Match candidates with enriched job postings"""
    try:
        logging.info("Starting candidate matching step")
        
        enriched_jobs = state.get("enriched_jobs", [])
        if not enriched_jobs:
            logging.warning("No enriched jobs to match")
            return {
                **state,
                "matches": [],
                "current_step": "matching_candidates"
            }
        
        candidate_matcher = CandidateMatcherAgent()
        result = candidate_matcher.exec()
        
        # Parse the result to get matches
        if isinstance(result, dict):
            matches = result.get('matches', [])
        elif isinstance(result, list):
            matches = result
        else:
            matches = []
            
        logging.info(f"Generated {len(matches)} matches")
        
        return {
            **state,
            "matches": matches,
            "current_step": "matching_candidates"
        }
        
    except Exception as e:
        logging.error(f"Error in match_candidates_step: {str(e)}")
        return {
            **state,
            "matches": [],
            "errors": state.get("errors", []) + [f"Matching error: {str(e)}"],
            "current_step": "matching_candidates"
        }

def create_job_matching_workflow():
    """Create the LangGraph workflow"""
    
    # Create the workflow graph with proper state schema
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("fetch_jobs", fetch_job_postings)
    workflow.add_node("enrich_jobs", enrich_job_postings_step)
    workflow.add_node("match_candidates", match_candidates_step)
    
    # Define the flow
    workflow.set_entry_point("fetch_jobs")
    workflow.add_edge("fetch_jobs", "enrich_jobs")
    workflow.add_edge("enrich_jobs", "match_candidates")
    workflow.add_edge("match_candidates", END)
    
    # Compile the workflow
    return workflow.compile()

# Usage
def run_job_matching_workflow():
    """Run the complete job matching workflow"""
    workflow = create_job_matching_workflow()
    
    # Create initial state as a dictionary
    initial_state: WorkflowState = {
        "job_postings": [],
        "enriched_jobs": [],
        "matches": [],
        "errors": [],
        "current_step": ""
    }
    
    result = workflow.invoke(initial_state)
    
    logging.info(f"Workflow completed. Generated {len(result['matches'])} matches")
    if result.get('errors'):
        logging.error(f"Workflow errors: {result['errors']}")
    
    return result

if __name__ == '__main__':
    result = run_job_matching_workflow()
    print(f"Workflow completed with {len(result['matches'])} matches")
