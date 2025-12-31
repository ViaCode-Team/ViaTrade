import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta, date
from domain.models.logic import TimeFrame
from typing import Optional, Dict


class BaseMoexClient:
    MAX_RECORDS = 500

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _get(self, session: aiohttp.ClientSession, url: str, params: Optional[Dict] = None) -> dict:
        try:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientResponseError as e:
            print(f"HTTP ошибка: {e.status} {e.message}")
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента: {e}")
        except asyncio.TimeoutError:
            print("Время запроса истекло")
        return {}

    async def get_all_instruments(self, session: aiohttp.ClientSession) -> list[str]:
        url = f"{self.base_url}.json"
        data = await self._get(session, url)
        securities = data.get("securities", {}).get("data", [])
        columns = data.get("securities", {}).get("columns", [])
        if not securities or "SECID" not in columns:
            return []
        idx = columns.index("SECID")
        return [row[idx] for row in securities if row[idx]]

    async def _load_candles_raw(
        self,
        session: aiohttp.ClientSession,
        ticker: str,
        interval: TimeFrame,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        url = f"{self.base_url}/{ticker}/candles.json"
        params = {
            "from": start.strftime("%Y-%m-%d"),
            "till": end.strftime("%Y-%m-%d"),
            "interval": interval.value,
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

    def _estimate_max_days(self, interval: TimeFrame) -> int:
        if interval == TimeFrame.DAY:
            return 500
        if interval == TimeFrame.HOUR:
            return 70
        if interval == TimeFrame.MIN10:
            return 12
        if interval == TimeFrame.MIN1:
            return 1
        if interval == TimeFrame.WEEK:
            return 3500
        if interval == TimeFrame.MONTH:
            return 15000
        return 500

    async def get_candles(
        self,
        session: aiohttp.ClientSession,
        ticker: str,
        interval: TimeFrame,
        from_date: Optional[str],
        till_date: Optional[str],
    ) -> pd.DataFrame:
        till = datetime.strptime(till_date, "%Y-%m-%d").date() if till_date else datetime.now().date()
        start = (
            datetime.strptime(from_date, "%Y-%m-%d").date()
            if from_date
            else till - timedelta(days=180)
        )

        total_days = (till - start).days
        max_days = self._estimate_max_days(interval)

        if total_days <= max_days:
            return await self._load_candles_raw(session, ticker, interval, start, till)

        frames = []
        cur = start
        while cur < till:
            end = min(cur + timedelta(days=max_days), till)
            df = await self._load_candles_raw(session, ticker, interval, cur, end)
            if not df.empty:
                frames.append(df)
            cur = end + timedelta(days=1)

        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
