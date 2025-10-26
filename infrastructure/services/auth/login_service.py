from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.auth_dto import LoginDto, TokenResponseDto
from application.interface.iauth_service import IAuthService
from application.interface.ipassword_hasher import IPasswordHasher
from domain.exceptions import InvalidCredentialsException
from application.interface.itoken_helper import ITokenHelper
from infrastructure.repositories.user import UserRepository


class LoginService(IAuthService):
    def __init__(
        self,
        session: AsyncSession,
        password_hasher: IPasswordHasher,
        token_helper: ITokenHelper,
    ) -> None:
        self.session = session
        self.password_hasher = password_hasher
        self.token_helper = token_helper
        self.user_repo = UserRepository(session)

    async def execute(self, dto: LoginDto) -> TokenResponseDto:
        user = await self.user_repo.get_by_login(dto.login)
        if not user:
            raise InvalidCredentialsException("Invalid login or password")

        if not self.password_hasher.verify_password(dto.password, user.hash_password):
            raise InvalidCredentialsException("Invalid login or password")

        tokens = await self.token_helper.create_tokens(user.id, user.login)

        return TokenResponseDto(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )