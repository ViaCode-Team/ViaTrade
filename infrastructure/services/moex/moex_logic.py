import pandas as pd
from datetime import datetime, timedelta
from domain.model import TimeFrame
from infrastructure.services.moex.moex_api import MoexApiClient


class MoexLogicService:
    MAX_RECORDS = 500

    def __init__(self):
        self.api = MoexApiClient()

    def get_candles_with_range(
        self,
        ticker: str,
        interval: TimeFrame = TimeFrame.DAY,
        from_date: str | None = None,
        till_date: str | None = None,
    ) -> pd.DataFrame:
        if till_date is None:
            till_date = datetime.now().date()
        else:
            till_date = datetime.strptime(till_date, "%Y-%m-%d").date()

        if from_date is None:
            from_date = till_date - timedelta(days=180)
        else:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()

        delta_days = (till_date - from_date).days
        max_days = self._estimate_max_days(interval)

        if delta_days <= max_days:
            return self.api.get_candles(ticker, interval, from_date, till_date)

        frames = []
        current_start = from_date
        while current_start < till_date:
            current_end = min(current_start + timedelta(days=max_days), till_date)
            df_part = self.api.get_candles(ticker, interval, current_start, current_end)
            if not df_part.empty:
                frames.append(df_part)
            current_start = current_end + timedelta(days=1)

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)

    def _estimate_max_days(self, interval: TimeFrame):
        if interval == TimeFrame.DAY:
            return 500
        if interval == TimeFrame.HOUR:
            return int(500 / 7)
        if interval == TimeFrame.MIN10:
            return int(500 / 39)
        if interval == TimeFrame.MIN1:
            return int(500 / 390)
        if interval == TimeFrame.WEEK:
            return 500 * 7
        if interval == TimeFrame.MONTH:
            return 500 * 30
        return 500
