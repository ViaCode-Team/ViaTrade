from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class ScreenerResult:
    TRADEDATE: datetime
    CLOSE: float
    EMA_12: float
    EMA_26: float
    MACD: float
    MACD_signal: float
    RSI: float
    ADX: float
    Stoch_K: float
    Stoch_D: float
    ATR: float
    Signal: SignalType
