from sqlalchemy.ext.asyncio import AsyncSession

from application.base.repository import BaseRepository
from domain.entity import TradeType


class TradeTypeRepository(BaseRepository[TradeType]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TradeType)
