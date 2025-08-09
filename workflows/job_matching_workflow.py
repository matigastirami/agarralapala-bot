from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from agents.job_seeker.agent import JobSeekerAgent
from agents.candidate_matcher.agent import CandidateMatcherAgent
from agents.common.tools.enrich_job_postings import enrich_job_postings
import logging

# Define the state schema
class WorkflowState:
    def __init__(self):
        self.job_postings = []
        self.enriched_jobs = []
        self.matches = []
        self.errors = []
        self.current_step = ""

# Node functions for the workflow
def fetch_job_postings(state: WorkflowState) -> WorkflowState:
    """Step 1: Fetch job postings using the job seeker agent"""
    try:
        logging.info("Starting job posting fetch step")
        state.current_step = "fetching_jobs"
        
        job_seeker = JobSeekerAgent()
        result = job_seeker.exec()
        
        # Parse the result to get job postings
        # This depends on how your job_seeker agent returns data
        if isinstance(result, dict):
            state.job_postings = result.get('job_postings', [])
        elif isinstance(result, list):
            state.job_postings = result
        else:
            state.job_postings = []
            
        logging.info(f"Fetched {len(state.job_postings)} job postings")
        
    except Exception as e:
        logging.error(f"Error in fetch_job_postings: {str(e)}")
        state.errors.append(f"Fetch error: {str(e)}")
    
    return state

def enrich_job_postings_step(state: WorkflowState) -> WorkflowState:
    """Step 2: Enrich job postings with detailed descriptions"""
    try:
        logging.info("Starting job enrichment step")
        state.current_step = "enriching_jobs"
        
        if not state.job_postings:
            logging.warning("No job postings to enrich")
            return state
        
        # Get job IDs to enrich
        job_ids = [job['id'] for job in state.job_postings if isinstance(job, dict) and 'id' in job]
        
        if not job_ids:
            logging.warning("No valid job IDs found for enrichment")
            return state
        
        # Use the enrich_job_postings tool
        enriched_results = enrich_job_postings(job_ids)
        state.enriched_jobs = enriched_results
        
        logging.info(f"Enriched {len(state.enriched_jobs)} job postings")
        
    except Exception as e:
        logging.error(f"Error in enrich_job_postings_step: {str(e)}")
        state.errors.append(f"Enrichment error: {str(e)}")
    
    return state

def match_candidates_step(state: WorkflowState) -> WorkflowState:
    """Step 3: Match candidates with enriched job postings"""
    try:
        logging.info("Starting candidate matching step")
        state.current_step = "matching_candidates"
        
        if not state.enriched_jobs:
            logging.warning("No enriched jobs to match")
            return state
        
        candidate_matcher = CandidateMatcherAgent()
        result = candidate_matcher.exec()
        
        # Parse the result to get matches
        if isinstance(result, dict):
            state.matches = result.get('matches', [])
        elif isinstance(result, list):
            state.matches = result
        else:
            state.matches = []
            
        logging.info(f"Generated {len(state.matches)} matches")
        
    except Exception as e:
        logging.error(f"Error in match_candidates_step: {str(e)}")
        state.errors.append(f"Matching error: {str(e)}")
    
    return state

def create_job_matching_workflow():
    """Create the LangGraph workflow"""
    
    # Create the workflow graph
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
    
    initial_state = WorkflowState()
    result = workflow.invoke(initial_state)
    
    logging.info(f"Workflow completed. Generated {len(result.matches)} matches")
    if result.errors:
        logging.error(f"Workflow errors: {result.errors}")
    
    return result
