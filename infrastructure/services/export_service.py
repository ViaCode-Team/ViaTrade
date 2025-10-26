import pandas as pd
from pathlib import Path


class ExportService:
    @staticmethod
    def export_to_csv(df: pd.DataFrame, ticker: str, interval: str, from_date: str, till_date: str, folder: str = "data"):
        Path(folder).mkdir(exist_ok=True)
        filename = f"{ticker}_{interval}_{from_date}_{till_date}.csv"
        path = Path(folder) / filename
        df.to_csv(path, index=False)
        return path
