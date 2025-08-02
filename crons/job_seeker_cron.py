from apscheduler.schedulers.background import BackgroundScheduler

def register_scheduler(job, trigger: str, **kwargs):
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, trigger, **kwargs)
    return scheduler

