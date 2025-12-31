from infrastructure.services.moex.moex_client import BaseMoexClient


class StocksClient(BaseMoexClient):
    def __init__(self):
        super().__init__("https://iss.moex.com/iss/engines/stock/markets/shares/securities")
