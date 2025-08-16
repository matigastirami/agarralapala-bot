import logging
from abc import ABC, abstractmethod
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class CronJob(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def interval_hours(self) -> int:
        pass
    
    @property
    @abstractmethod
    def start_time(self) -> str:
        """Start time in HH:MM format (24-hour)"""
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
            # Parse start time
            try:
                hour, minute = map(int, job.start_time.split(':'))
                start_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If start time has passed today, schedule for tomorrow
                if start_time <= datetime.now():
                    start_time = start_time.replace(day=start_time.day + 1)
                
                # Schedule job with both interval and start time
                self.scheduler.add_job(
                    job.run,
                    'interval',
                    hours=job.interval_hours,
                    start_date=start_time,
                    id=job.name,
                    replace_existing=True
                )
                logging.info(f"[CronManager] Scheduled job {job.name} every {job.interval_hours} hours starting at {start_time.strftime('%H:%M')}")
                
            except Exception as e:
                logging.error(f"[CronManager] Error scheduling job {job.name}: {e}")
                # Fallback to simple interval scheduling
                self.scheduler.add_job(
                    job.run,
                    'interval',
                    hours=job.interval_hours,
                    id=job.name,
                    replace_existing=True
                )
                logging.info(f"[CronManager] Scheduled job {job.name} every {job.interval_hours} hours (fallback)")

        self.scheduler.start()
        logging.info("[CronManager] Scheduler started")

    def shutdown(self):
        self.scheduler.shutdown()
        logging.info("[CronManager] Scheduler stopped")
