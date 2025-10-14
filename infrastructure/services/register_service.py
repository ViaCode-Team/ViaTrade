from sqlalchemy.ext.asyncio import AsyncSession

from application.interface.iauth_service import IAuthService
from application.interface.ipassword_hasher import IPasswordHasher
from domain.entity import User
from domain.exceptions import UserAlreadyExistsException
from application.dto.auth_dto import RegisterDto, TokenResponseDto
from infrastructure.interface.itoken_manager import ITokenManager
from infrastructure.repositories.user import UserRepository


class RegisterService(IAuthService):
    def __init__(
        self,
        session: AsyncSession,
        password_hasher: IPasswordHasher,
        token_manager: ITokenManager,
    ) -> None:
        self.session = session
        self.password_hasher = password_hasher
        self.token_manager = token_manager
        self.user_repo = UserRepository(session)

    async def execute(self, dto: RegisterDto) -> TokenResponseDto:
        existing_user = await self.user_repo.get_by_login(dto.login)
        if existing_user:
            raise UserAlreadyExistsException(f"User with login '{dto.login}' already exists")

        hashed_password = self.password_hasher.hash_password(dto.password)
        user = User(login=dto.login, hash_password=hashed_password)

        new_user = await self.user_repo.add(user)
        tokens = await self.token_manager.create_tokens(new_user.id, new_user.login)

        return TokenResponseDto(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )