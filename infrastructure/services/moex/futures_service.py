from infrastructure.services.moex.moex_client import BaseMoexClient


class FuturesClient(BaseMoexClient):
    def __init__(self):
        super().__init__("https://iss.moex.com/iss/engines/futures/markets/forts/securities")
