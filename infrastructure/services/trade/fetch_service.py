from typing import List
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from domain.models.logic import InstumentType, TimeFrame
from infrastructure.services.export_service import ExportService
from infrastructure.services.moex.moex_facade import MoexFacade
from infrastructure.services.moex.moex_logic import MoexDataService


class TradeFetchService:
    def __init__(self, cron: CronTrigger, interval: TimeFrame = TimeFrame.HOUR):
        self.cron = cron
        self.interval = interval
        self.facade = MoexFacade()
        self.data = MoexDataService()

    async def __call__(self) -> None:
        stocks: List[str] = await self.facade.get_all(InstumentType.STOCKS.value)
        futures: List[str] = await self.facade.get_all(InstumentType.FUTURES.value)

        targets_stocks = stocks[:10]
        targets_futures = futures[:10]

        today = datetime.now().date().strftime("%Y-%m-%d")
        interval_name = self.interval.name

        for ticker in targets_stocks:
            df = await self.data.get_last_half_year(ticker, self.interval)
            if not df.empty:
                ExportService.export_to_csv(
                    df=df,
                    ticker=ticker,
                    interval=interval_name,
                    from_date=df["begin"].min().strftime("%Y-%m-%d"),
                    till_date=df["begin"].max().strftime("%Y-%m-%d"),
                    folder="data/stocks"
                )

        for ticker in targets_futures:
            df = await self.data.get_last_half_year(ticker, self.interval)
            if not df.empty:
                ExportService.export_to_csv(
                    df=df,
                    ticker=ticker,
                    interval=interval_name,
                    from_date=df["begin"].min().strftime("%Y-%m-%d"),
                    till_date=df["begin"].max().strftime("%Y-%m-%d"),
                    folder="data/futures"
                )

        print(f"{datetime.now()} - Trade fetch completed")
