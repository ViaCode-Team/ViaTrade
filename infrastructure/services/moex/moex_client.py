import aiohttp
import pandas as pd
from datetime import date
from domain.model import TimeFrame


class MoexApiClient:
    STOCKS_URL = "https://iss.moex.com/iss/engines/stock/markets/shares/securities"
    FUTURES_URL = "https://iss.moex.com/iss/engines/futures/markets/forts/securities"

    async def _get(self, session: aiohttp.ClientSession, url: str, params: dict | None = None) -> dict:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_candles(self, session: aiohttp.ClientSession, ticker: str, interval: TimeFrame, from_date: date, till_date: date, is_futures: bool) -> pd.DataFrame:
        base_url = self.FUTURES_URL if is_futures else self.STOCKS_URL
        url = f"{base_url}/{ticker}/candles.json"
        params = {
            "from": from_date.strftime("%Y-%m-%d"),
            "till": till_date.strftime("%Y-%m-%d"),
            "interval": interval.value
        }

        data = await self._get(session, url, params)
        candles = data.get("candles", {}).get("data", [])
        columns = data.get("candles", {}).get("columns", [])

        if not candles:
            return pd.DataFrame()

        df = pd.DataFrame([{k: row[i] for i, k in enumerate(columns)} for row in candles])
        if "begin" in df.columns:
            df["begin"] = pd.to_datetime(df["begin"])
        if "end" in df.columns:
            df["end"] = pd.to_datetime(df["end"])

        return df[["begin", "open", "close", "high", "low", "volume"]]

    async def get_instruments_list(self, is_futures: bool) -> list[str]:
        base_url = self.FUTURES_URL if is_futures else self.STOCKS_URL
        url = f"{base_url}.json"

        async with aiohttp.ClientSession() as session:
            data = await self._get(session, url)
            securities = data.get("securities", {}).get("data", [])
            columns = data.get("securities", {}).get("columns", [])
            if not securities:
                return []

            try:
                secid_index = columns.index("SECID")
                return [row[secid_index] for row in securities if row[secid_index]]
            except (ValueError, IndexError):
                return []
