from sqlalchemy.ext.asyncio import AsyncSession

from application.base.repository import BaseRepository
from domain.entity import TradeCode, UserTradeCode


class TradeCodeRepository(BaseRepository[TradeCode]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TradeCode)


class UserTradeCodeRepository(BaseRepository[UserTradeCode]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserTradeCode)
