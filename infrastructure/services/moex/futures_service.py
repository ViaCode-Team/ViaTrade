from infrastructure.services.moex.moex_client import MoexApiClient


class FuturesService:
    def __init__(self):
        self.api = MoexApiClient()

    async def get_all_futures(self) -> list[str]:
        return await self.api.get_instruments_list(is_futures=True)
