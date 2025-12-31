# Trade Models
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SignalType(Enum):
    BUY = "Buy"
    SELL = "Sell"
    HOLD = "Hold"

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

@dataclass
class Candle:
    open: float
    close: float
    high: float
    low: float
    volume: float

class InstumentType(Enum):
    STOCKS = "stocks"
    FUTURES = "futures"


# Moex Models
class TimeFrame(Enum):
    MIN1 = 1
    MIN10 = 10
    HOUR = 60
    DAY = 24
    WEEK = 7
    MONTH = 31

