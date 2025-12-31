from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import TokenInvalidException
from application.dto.auth_dto import RefreshTokenDto, TokenResponseDto
from application.interface.itoken_helper import ITokenHelper


class RefreshTokenService:
    def __init__(
        self,
        session: AsyncSession,
        token_helper: ITokenHelper,
    ) -> None:
        self.session = session
        self.token_helper = token_helper

    async def execute(self, dto: RefreshTokenDto) -> TokenResponseDto:
        try:
            payload = await self.token_helper.verify_refresh_token(dto.refresh_token)
        except Exception as e:
            raise TokenInvalidException(f"Invalid refresh token: {str(e)}")

        tokens = await self.token_helper.create_tokens(payload.user_id, payload.login)

        return TokenResponseDto(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )
