from agents.job_seeker.agent import JobSeekerAgent
from crons.cron_manager import CronJob


class JobSeekerCron(CronJob):
    def __init__(self):
        self.agent = JobSeekerAgent()

    @property
    def name(self) -> str:
        return "job_seeker_agent_cron"

    @property
    def interval_hours(self) -> int:
        return 24

    def run(self):
        self.agent.exec()