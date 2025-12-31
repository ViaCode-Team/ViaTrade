from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from domain.models.system import BackgroundTask

class BackgroundService:
    def __init__(self, name: str, func: BackgroundTask, cron: CronTrigger):
        self.name = name
        self.func = func
        self.cron = cron
        self.job_id = name

    async def run(self) -> None:
        await self.func()

    def register(self, scheduler: AsyncIOScheduler) -> None:
        scheduler.add_job(self.run, self.cron, id=self.job_id)

    def force_run(self, scheduler: AsyncIOScheduler) -> None:
        job = scheduler.get_job(self.job_id)
        if job is not None:
            scheduler.modify_job(job.id, next_run_time=datetime.now())
