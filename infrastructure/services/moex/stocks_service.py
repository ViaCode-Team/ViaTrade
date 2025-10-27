from infrastructure.services.moex.moex_client import MoexApiClient


class StocksService:
    def __init__(self):
        self.api = MoexApiClient()

    async def get_all_stocks(self) -> list[str]:
        return await self.api.get_instruments_list(is_futures=False)
