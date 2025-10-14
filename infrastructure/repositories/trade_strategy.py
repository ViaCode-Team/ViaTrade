from sqlalchemy.ext.asyncio import AsyncSession

from application.base.repository import BaseRepository
from domain.entity import TradeStrategy, UserTradeStrategy


class TradeStrategyRepository(BaseRepository[TradeStrategy]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TradeStrategy)


class UserTradeStrategyRepository(BaseRepository[UserTradeStrategy]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserTradeStrategy)
