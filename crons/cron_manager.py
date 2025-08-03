import logging
from abc import ABC, abstractmethod

from apscheduler.schedulers.background import BackgroundScheduler

class CronJob(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def interval_hours(self) -> int:
        pass

    @abstractmethod
    def run(self):
        pass

class CronManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = []

    def register(self, job: CronJob):
        self.jobs.append(job)
        logging.info(f"[CronManager] Registered job {job}")

    def start(self):
        for job in self.jobs:
            self.scheduler.add_job(
                job.run,
                'interval',
                hours=job.interval_hours,
                id=job.name,
                replace_existing=True
            )
            logging.info(f"[CronManager] Scheduled job {job.name} every {job.interval_hours} hours")

        self.scheduler.start()
        logging.info("[CronManger] Scheduler started")

    def shutdown(self):
        self.scheduler.shutdown()
        logging.info("[CronManager] Scheduler stopped")
