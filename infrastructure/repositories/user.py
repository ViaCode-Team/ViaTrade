from sqlalchemy.ext.asyncio import AsyncSession

from application.base.repository import BaseRepository
from domain.entity import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)
