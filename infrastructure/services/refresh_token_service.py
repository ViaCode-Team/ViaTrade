from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import TokenInvalidException
from application.dto.auth_dto import RefreshTokenDto, TokenResponseDto
from infrastructure.interface.itoken_manager import ITokenManager


class RefreshTokenUseCase:
    def __init__(
        self,
        session: AsyncSession,
        token_manager: ITokenManager,
    ) -> None:
        self.session = session
        self.token_manager = token_manager

    async def execute(self, dto: RefreshTokenDto) -> TokenResponseDto:
        try:
            payload = await self.token_manager.verify_refresh_token(dto.refresh_token)
        except Exception as e:
            raise TokenInvalidException(f"Invalid refresh token: {str(e)}")

        tokens = await self.token_manager.create_tokens(payload.user_id, payload.login)

        return TokenResponseDto(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )