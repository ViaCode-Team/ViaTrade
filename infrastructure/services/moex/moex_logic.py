import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from domain.model import TimeFrame
from infrastructure.services.moex.moex_client import MoexApiClient


class MoexLogicService:
    MAX_RECORDS = 500

    def __init__(self):
        self.api = MoexApiClient()

    async def get_candles(self, ticker: str, interval: TimeFrame, from_date: str | None, till_date: str | None, is_futures: bool) -> pd.DataFrame:
        till_date = datetime.strptime(till_date, "%Y-%m-%d").date() if till_date else datetime.now().date()
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else till_date - timedelta(days=180)

        total_days = (till_date - from_date).days
        max_days = self._estimate_max_days(interval)

        async with aiohttp.ClientSession() as session:
            if total_days <= max_days:
                return await self.api.get_candles(session, ticker, interval, from_date, till_date, is_futures)

            frames = []
            start = from_date
            while start < till_date:
                end = min(start + timedelta(days=max_days), till_date)
                df_part = await self.api.get_candles(session, ticker, interval, start, end, is_futures)
                if not df_part.empty:
                    frames.append(df_part)
                start = end + timedelta(days=1)

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    async def get_unified_candles(self, ticker: str, interval: TimeFrame, from_date: str | None = None, till_date: str | None = None, instrument_type: str = "stock") -> pd.DataFrame:
        is_futures = instrument_type.lower() == "futures"
        return await self.get_candles(ticker, interval, from_date, till_date, is_futures)

    def _estimate_max_days(self, interval: TimeFrame) -> int:
        if interval == TimeFrame.DAY:
            return 500
        if interval == TimeFrame.HOUR:
            return int(500 / 7)
        if interval == TimeFrame.MIN10:
            return int(500 / 39)
        if interval == TimeFrame.MIN1:
            return int(500 / 390)
        if interval == TimeFrame.WEEK:
            return 3500
        if interval == TimeFrame.MONTH:
            return 15000
        return 500
