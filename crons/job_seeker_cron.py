from agents.job_seeker.agent import JobSeekerAgent
from crons.cron_manager import CronJob
from common.config.config import CRON_JOB_SEEKER_INTERVAL_HOURS, CRON_JOB_SEEKER_START_TIME


class JobSeekerCron(CronJob):
    def __init__(self):
        self.agent = JobSeekerAgent()

    @property
    def name(self) -> str:
        return "job_seeker_agent_cron"

    @property
    def interval_hours(self) -> int:
        return CRON_JOB_SEEKER_INTERVAL_HOURS
    
    @property
    def start_time(self) -> str:
        return CRON_JOB_SEEKER_START_TIME

    def run(self):
        self.agent.exec()