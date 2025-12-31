import aiohttp
import pandas as pd
from domain.exceptions import InvalidInstrumentCodeError
from domain.models.logic import InstumentType, TimeFrame
from infrastructure.services.moex.futures_service import FuturesClient
from infrastructure.services.moex.stocks_service import StocksClient
from infrastructure.services.moex.moex_client import BaseMoexClient
import asyncio

class MoexFacade:
    TIMEOUT = 60

    def __init__(self):
        self.clients = {
            InstumentType.STOCKS.value: StocksClient(),
            InstumentType.FUTURES.value: FuturesClient()
        }

    def _get_client(self, instrument_type: str) -> BaseMoexClient:
        key = instrument_type.lower()
        return self.clients.get(key)

    async def get_all(self, instrument_type: str) -> list[str]:
        client = self._get_client(instrument_type)
        if not client:
            return []
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)) as session:
            return await client.get_all_instruments(session)

    async def get_candles(self, instrument_type: str, ticker: str, interval: TimeFrame, from_date: str | None, till_date: str | None) -> pd.DataFrame:
        client = self._get_client(instrument_type)
        if not client:
            return pd.DataFrame()
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)) as session:
            return await client.get_candles(session, ticker, interval, from_date, till_date)

    async def get_candles_auto_detect(self, ticker: str, interval: TimeFrame, from_date: str | None, till_date: str | None) -> pd.DataFrame:
        stocks_client = self._get_client(InstumentType.STOCKS.value)
        futures_client = self._get_client(InstumentType.FUTURES.value)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.TIMEOUT)) as session:
            try:
                stocks_task = stocks_client.get_all_instruments(session)
                futures_task = futures_client.get_all_instruments(session)
                stocks_list, futures_list = await asyncio.gather(stocks_task, futures_task)
            except Exception as e:
                print(f"Ошибка при получении списка инструментов: {e}")
                stocks_list, futures_list = [], []

            ticker_upper = ticker.upper()
            if ticker_upper in stocks_list:
                return await stocks_client.get_candles(session, ticker_upper, interval, from_date, till_date)
            if ticker_upper in futures_list:
                return await futures_client.get_candles(session, ticker_upper, interval, from_date, till_date)
            raise InvalidInstrumentCodeError("Undefined code or no data in API")
