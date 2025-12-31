from typing import Optional
import aiohttp
import pandas as pd
import asyncio
import logging
from domain.exceptions import InvalidInstrumentCodeError
from domain.models.logic import InstumentType, TimeFrame
from infrastructure.services.moex.futures_service import FuturesClient
from infrastructure.services.moex.stocks_service import StocksClient
from infrastructure.services.moex.moex_client import BaseMoexClient

logger = logging.getLogger(__name__)


class MoexFacade:
    TIMEOUT = 60  # Request timeout in seconds

    def __init__(self):
        # Mapping of instrument types to their respective clients
        self.clients = {
            InstumentType.STOCKS.value: StocksClient(),
            InstumentType.FUTURES.value: FuturesClient(),
        }

    def _get_client(self, instrument_type: str) -> Optional[BaseMoexClient]:
        """Return the client for the given instrument type, or None if invalid."""
        key = instrument_type.lower()
        client = self.clients.get(key)
        if not client:
            logger.warning("Client for instrument type '%s' not found", instrument_type)
        return client

    async def get_all(self, instrument_type: str) -> list[str]:
        """Fetch all instruments for a given type."""
        client = self._get_client(instrument_type)
        if not client:
            return []
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)
        ) as session:
            try:
                instruments = await client.get_all_instruments(session)
                logger.info(
                    "Fetched %d instruments for %s", len(instruments), instrument_type
                )
                return instruments
            except Exception as e:
                logger.error(
                    "Failed to fetch instruments for %s: %s",
                    instrument_type,
                    e,
                    exc_info=True,
                )
                return []

    async def get_candles(
        self,
        instrument_type: str,
        ticker: str,
        interval: TimeFrame,
        from_date: str | None,
        till_date: str | None,
    ) -> pd.DataFrame:
        """Fetch candle data for a given ticker and interval."""
        client = self._get_client(instrument_type)
        if not client:
            return pd.DataFrame()
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)
        ) as session:
            try:
                df = await client.get_candles(
                    session, ticker, interval, from_date, till_date
                )
                logger.info(
                    "Fetched %d candles for %s (%s)", len(df), ticker, instrument_type
                )
                return df
            except Exception as e:
                logger.error(
                    "Failed to fetch candles for %s (%s): %s",
                    ticker,
                    instrument_type,
                    e,
                    exc_info=True,
                )
                return pd.DataFrame()

    async def get_candles_auto_detect(
        self,
        ticker: str,
        interval: TimeFrame,
        from_date: str | None,
        till_date: str | None,
    ) -> pd.DataFrame:
        """
        Auto-detect whether the ticker is a stock or future,
        then fetch candle data accordingly.
        """
        stocks_client = self._get_client(InstumentType.STOCKS.value)
        futures_client = self._get_client(InstumentType.FUTURES.value)
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)
        ) as session:
            try:
                # Fetch lists of all instruments concurrently
                stocks_task = stocks_client.get_all_instruments(session)
                futures_task = futures_client.get_all_instruments(session)
                stocks_list, futures_list = await asyncio.gather(
                    stocks_task, futures_task
                )
                logger.info(
                    "Auto-detect: fetched %d stocks and %d futures",
                    len(stocks_list),
                    len(futures_list),
                )
            except Exception as e:
                logger.error(
                    "Failed to fetch instruments for auto-detect: %s", e, exc_info=True
                )
                stocks_list, futures_list = [], []

            ticker_upper = ticker.upper()
            if ticker_upper in stocks_list:
                return await stocks_client.get_candles(
                    session, ticker_upper, interval, from_date, till_date
                )
            if ticker_upper in futures_list:
                return await futures_client.get_candles(
                    session, ticker_upper, interval, from_date, till_date
                )

            logger.error("Undefined instrument code or no data: %s", ticker)
            raise InvalidInstrumentCodeError(
                f"Undefined code or no data in API: {ticker}"
            )
