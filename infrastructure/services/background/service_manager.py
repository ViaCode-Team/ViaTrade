from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from infrastructure.services.background.background_service import BackgroundService

class ServiceManager:
    scheduler: AsyncIOScheduler
    services: List[BackgroundService]

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.services = []

    def add_service(self, service: BackgroundService) -> None:
        self.services.append(service)
        service.register(self.scheduler)

    def start(self) -> None:
        self.scheduler.start()

    def run_now(self, name: str) -> None:
        for s in self.services:
            if s.name == name:
                s.force_run(self.scheduler)
                break
