import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta, date
from domain.models.logic import TimeFrame
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class BaseMoexClient:
    MAX_RECORDS = 500
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def _get(
        self, session: aiohttp.ClientSession, url: str, params: Optional[Dict] = None
    ) -> dict:
        """Perform GET request with retries on network/timeout errors."""
        for attempt in range(1, self.RETRY_COUNT + 1):
            try:
                async with session.get(url, params=params) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except (
                aiohttp.ClientError,
                aiohttp.ClientResponseError,
                asyncio.TimeoutError,
            ) as e:
                if attempt == self.RETRY_COUNT:
                    logger.error(
                        "Request to %s failed: %s, all retries exhausted", url, e
                    )
                    return {}
                else:
                    logger.warning(
                        "Request to %s failed: %s, retrying in %ds (attempt %d)",
                        url,
                        e,
                        self.RETRY_DELAY,
                        attempt,
                    )
                    await asyncio.sleep(self.RETRY_DELAY)
        return {}

    async def get_all_instruments(self, session: aiohttp.ClientSession) -> list[str]:
        """Fetch all available instruments from MOEX."""
        url = f"{self.base_url}.json"
        data = await self._get(session, url)
        securities = data.get("securities", {}).get("data", [])
        columns = data.get("securities", {}).get("columns", [])
        if not securities or "SECID" not in columns:
            logger.warning("No securities found at %s", url)
            return []
        idx = columns.index("SECID")
        instruments = [row[idx] for row in securities if row[idx]]
        logger.info("Fetched %d instruments from %s", len(instruments), url)
        return instruments

    async def _load_candles_raw(
        self,
        session: aiohttp.ClientSession,
        ticker: str,
        interval: TimeFrame,
        start: date,
        end: date,
    ) -> pd.DataFrame:
        """Fetch candle data for a single date range."""
        url = f"{self.base_url}/{ticker}/candles.json"
        params = {
            "from": start.strftime("%Y-%m-%d"),
            "till": end.strftime("%Y-%m-%d"),
            "interval": interval.value,
        }
        logger.debug("Loading candles from %s with params %s", url, params)
        data = await self._get(session, url, params)
        candles = data.get("candles", {}).get("data", [])
        columns = data.get("candles", {}).get("columns", [])
        if not candles:
            logger.warning("No candle data returned for %s", ticker)
            return pd.DataFrame()

        df = pd.DataFrame(
            [{k: row[i] for i, k in enumerate(columns)} for row in candles]
        )
        if "begin" in df.columns:
            df["begin"] = pd.to_datetime(df["begin"])
        if "end" in df.columns:
            df["end"] = pd.to_datetime(df["end"])
        return df[["begin", "open", "close", "high", "low", "volume"]]

    def _estimate_max_days(self, interval: TimeFrame) -> int:
        """Estimate the maximum number of days per request for the given interval."""
        mapping = {
            TimeFrame.DAY: 500,
            TimeFrame.HOUR: 70,
            TimeFrame.MIN10: 12,
            TimeFrame.MIN1: 1,
            TimeFrame.WEEK: 3500,
            TimeFrame.MONTH: 15000,
        }
        return mapping.get(interval, 500)

    async def get_candles(
        self,
        session: aiohttp.ClientSession,
        ticker: str,
        interval: TimeFrame,
        from_date: Optional[str],
        till_date: Optional[str],
    ) -> pd.DataFrame:
        """Fetch candle data, splitting into multiple requests if needed."""
        till = (
            datetime.strptime(till_date, "%Y-%m-%d").date()
            if till_date
            else datetime.now().date()
        )
        start = (
            datetime.strptime(from_date, "%Y-%m-%d").date()
            if from_date
            else till - timedelta(days=180)
        )

        total_days = (till - start).days
        max_days = self._estimate_max_days(interval)

        logger.info(
            "Fetching candles for %s from %s to %s (total %d days, max per request %d)",
            ticker,
            start,
            till,
            total_days,
            max_days,
        )

        if total_days <= max_days:
            return await self._load_candles_raw(session, ticker, interval, start, till)

        # Split the request into multiple chunks if the range is too large
        frames = []
        cur = start
        while cur < till:
            end = min(cur + timedelta(days=max_days), till)
            df = await self._load_candles_raw(session, ticker, interval, cur, end)
            if not df.empty:
                frames.append(df)
            cur = end + timedelta(days=1)

        if not frames:
            logger.warning("No candle data found for %s", ticker)
            return pd.DataFrame()

        logger.info("Fetched candle data for %s in %d chunks", ticker, len(frames))
        return pd.concat(frames, ignore_index=True)
