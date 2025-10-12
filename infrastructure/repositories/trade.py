from sqlalchemy.ext.asyncio import AsyncSession

from application.base.repository import BaseRepository
from domain.entity import Trade


class TradeRepository(BaseRepository[Trade]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Trade)
