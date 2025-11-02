import pandas as pd
from domain.exceptions import InvalidInstrumentCodeError
from domain.model import InstumentType, TimeFrame
from infrastructure.services.moex.futures_service import FuturesClient
from infrastructure.services.moex.moex_client import BaseMoexClient
from infrastructure.services.moex.stocks_service import StocksClient
    

class MoexFacade:
    def __init__(self):
        self.clients = {
            InstumentType.STOCKS.value : StocksClient(),
            InstumentType.FUTURES.value : FuturesClient()
        }

    def _get_client(self, instrument_type: str) -> BaseMoexClient:
        key = instrument_type.lower()
        return self.clients.get(key)

    async def get_all(self, instrument_type: str) -> list[str]:
        client = self._get_client(instrument_type)
        if client is None:
            return []
        return await client.get_all_instruments()

    async def get_candles(self, instrument_type: str, ticker: str, interval: TimeFrame, from_date: str | None, till_date: str | None) -> pd.DataFrame:
        client = self._get_client(instrument_type)
        if client is None:
            return pd.DataFrame()
        return await client.get_candles(ticker, interval, from_date, till_date)
    
    
    async def get_candles_auto_detect(self, ticker: str, interval: TimeFrame, from_date: str | None, till_date: str | None) -> pd.DataFrame:
        stocks_client = self._get_client(InstumentType.STOCKS.value)
        futures_client = self._get_client(InstumentType.FUTURES.value)

        stocks_task = stocks_client.get_all_instruments()
        futures_task = futures_client.get_all_instruments()

        stocks_list, futures_list = await stocks_task, await futures_task

        ticker_upper = ticker.upper()

        if ticker_upper in stocks_list:
            return await stocks_client.get_candles(ticker_upper, interval, from_date, till_date)

        if ticker_upper in futures_list:
            return await futures_client.get_candles(ticker_upper, interval, from_date, till_date)

        raise InvalidInstrumentCodeError("Undefinde code or not data in API")
