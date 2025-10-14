from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.interface.itoken_manager import ITokenManager


class LogoutUseCase:
    def __init__(
        self,
        session: AsyncSession,
        token_manager: ITokenManager,
    ) -> None:
        self.session = session
        self.token_manager = token_manager

    async def execute(self, access_token: str) -> None:
        await self.token_manager.revoke_access_token(access_token)