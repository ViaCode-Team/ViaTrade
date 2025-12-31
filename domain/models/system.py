from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Protocol

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

# Background
class BackgroundTask(Protocol):
    async def __call__(self) -> Awaitable[None]:
        ...

