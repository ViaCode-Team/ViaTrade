from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.base.repository import BaseRepository
from domain.entity import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_login(self, login: str) -> User | None:
        stmt = select(User).where(User.login == login)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
