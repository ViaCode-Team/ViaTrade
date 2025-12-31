from datetime import datetime, timedelta
import pandas as pd
from domain.models.logic import TimeFrame
from infrastructure.services.moex.moex_facade import MoexFacade
import asyncio
import logging

logger = logging.getLogger(__name__)


class MoexDataService:
    RETRY_COUNT = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self):
        self.facade = MoexFacade()

    async def get_last_half_year(
        self, ticker: str, interval: TimeFrame
    ) -> pd.DataFrame:
        """Fetch candle data for the last half year with retries on failure."""
        today = datetime.now().date()
        half_year_ago = today - timedelta(days=180)
        from_date = half_year_ago.strftime("%Y-%m-%d")
        till_date = today.strftime("%Y-%m-%d")

        df: pd.DataFrame = pd.DataFrame()  # default empty DataFrame
        for attempt in range(1, self.RETRY_COUNT + 1):
            try:
                logger.info("Fetching data for %s, attempt %d", ticker, attempt)
                df = await self.facade.get_candles_auto_detect(
                    ticker=ticker,
                    interval=interval,
                    from_date=from_date,
                    till_date=till_date,
                )
                logger.info("Successfully fetched data for %s", ticker)
                return df
            except Exception as e:
                logger.warning(
                    "Error fetching data for %s: %s, retrying in %ds (attempt %d)",
                    ticker,
                    e,
                    self.RETRY_DELAY,
                    attempt,
                )
                await asyncio.sleep(self.RETRY_DELAY)

        # If all attempts fail, return empty DataFrame
        logger.error(
            "Failed to fetch data for %s after %d attempts", ticker, self.RETRY_COUNT
        )
        return df
