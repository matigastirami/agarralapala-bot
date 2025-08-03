from agents.job_seeker.agent import exec_jobs_agent
from crons.cron_manager import CronJob


class JobSeekerCron(CronJob):
    @property
    def name(self) -> str:
        return "job_seeker_agent_cron"

    @property
    def interval_hours(self) -> int:
        return 24

    def run(self):
        exec_jobs_agent()