from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.itoken_helper import ITokenHelper


class LogoutUseCase:
    def __init__(
        self,
        session: AsyncSession,
        token_helper: ITokenHelper,
    ) -> None:
        self.session = session
        self.token_helper = token_helper

    async def execute(self, access_token: str) -> None:
        await self.token_helper.revoke_access_token(access_token)