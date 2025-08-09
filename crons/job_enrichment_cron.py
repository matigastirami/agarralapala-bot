from crons.cron_manager import CronJob
from workflows.job_matching_workflow import run_job_matching_workflow
import logging

class JobEnrichmentCron(CronJob):
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return "job_enrichment_workflow_cron"

    @property
    def interval_hours(self) -> int:
        return 24  # Run once daily

    def run(self):
        logging.info("Starting job enrichment workflow")
        try:
            result = run_job_matching_workflow()
            logging.info(f"Job enrichment workflow completed successfully. Generated {len(result.matches)} matches")
        except Exception as e:
            logging.error(f"Job enrichment workflow failed: {str(e)}")
