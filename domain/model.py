from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Trade Models
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

# JWT Models
@dataclass
class TokenPair:
    access_token: str
    refresh_token: str

@dataclass
class TokenPayload:
    user_id: int
    login: str
    exp: datetime
    iat: datetime

