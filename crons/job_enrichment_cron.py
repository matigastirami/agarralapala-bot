from crons.cron_manager import CronJob
from workflows.job_matching_workflow import run_job_matching_workflow
from common.config.config import CRON_JOB_ENRICHMENT_INTERVAL_HOURS, CRON_JOB_ENRICHMENT_START_TIME
import logging

class JobEnrichmentCron(CronJob):
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "job_enrichment_workflow_cron"

    @property
    def interval_hours(self) -> int:
        return CRON_JOB_ENRICHMENT_INTERVAL_HOURS
    
    @property
    def start_time(self) -> str:
        return CRON_JOB_ENRICHMENT_START_TIME

    def run(self):
        logging.info("Starting job enrichment workflow")
        try:
            result = run_job_matching_workflow()
            logging.info(f"Job enrichment workflow completed successfully. Generated {len(result['matches'])} matches")
        except Exception as e:
            logging.error(f"Job enrichment workflow failed: {str(e)}")
