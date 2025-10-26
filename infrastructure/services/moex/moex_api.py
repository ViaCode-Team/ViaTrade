import requests
import pandas as pd
from datetime import datetime, timedelta

from domain.model import TimeFrame

class MoexApiClient:
    BASE_URL = "https://iss.moex.com/iss/engines/stock/markets/shares/securities"

    def get_candles(self, ticker: str, interval: TimeFrame, from_date: datetime, till_date: datetime):
        params = {
            "from": from_date.strftime("%Y-%m-%d"),
            "till": till_date.strftime("%Y-%m-%d"),
            "interval": interval.value,
        }

        url = f"{self.BASE_URL}/{ticker}/candles.json"
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        candles = data.get("candles", {}).get("data", [])
        columns = data.get("candles", {}).get("columns", [])
        if not candles:
            return pd.DataFrame()

        df = pd.DataFrame(candles, columns=columns)
        if "begin" in df:
            df["begin"] = pd.to_datetime(df["begin"])
        if "end" in df:
            df["end"] = pd.to_datetime(df["end"])
        return df[["begin", "open", "close", "high", "low", "volume"]]