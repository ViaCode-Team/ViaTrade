from datetime import datetime, timedelta
import pandas as pd
from domain.models.logic import TimeFrame
from infrastructure.services.moex.moex_facade import MoexFacade


class MoexDataService:
    def __init__(self):
        self.facade = MoexFacade()

    async def get_last_half_year(self, ticker: str, interval: TimeFrame) -> pd.DataFrame:
        today = datetime.now().date()
        half_year_ago = today - timedelta(days=180)

        from_date = half_year_ago.strftime("%Y-%m-%d")
        till_date = today.strftime("%Y-%m-%d")

        return await self.facade.get_candles_auto_detect(
            ticker=ticker,
            interval=interval,
            from_date=from_date,
            till_date=till_date
        )
