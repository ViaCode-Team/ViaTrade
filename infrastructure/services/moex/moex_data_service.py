from datetime import datetime, timedelta
import pandas as pd
from domain.models.logic import TimeFrame
from infrastructure.services.moex.moex_facade import MoexFacade
import asyncio

class MoexDataService:
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # сек

    def __init__(self):
        self.facade = MoexFacade()

    async def get_last_half_year(self, ticker: str, interval: TimeFrame) -> pd.DataFrame:
        today = datetime.now().date()
        half_year_ago = today - timedelta(days=180)
        from_date = half_year_ago.strftime("%Y-%m-%d")
        till_date = today.strftime("%Y-%m-%d")

        for attempt in range(1, self.RETRY_COUNT + 1):
            try:
                df = await self.facade.get_candles_auto_detect(
                    ticker=ticker,
                    interval=interval,
                    from_date=from_date,
                    till_date=till_date
                )
                return df
            except Exception as e:
                if attempt == self.RETRY_COUNT:
                    print(f"Ошибка получения данных по {ticker}: {e}")
                    return pd.DataFrame()
                else:
                    print(f"Ошибка получения данных по {ticker}: {e}, повтор через {self.RETRY_DELAY}с (попытка {attempt})")
                    await asyncio.sleep(self.RETRY_DELAY)
