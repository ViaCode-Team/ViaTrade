from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from application.dto.auth_dto import RegisterDto, LoginDto, RefreshTokenDto, TokenResponseDto
from application.interface.itoken_helper import ITokenHelper
from domain.exceptions import AuthException

from infrastructure.security.jwt_token_helper import JwtTokenHelper
from infrastructure.security.password_hasher import PasswordHasher
from infrastructure.services.login_service import LoginService
from infrastructure.services.logout_service import LogoutService
from infrastructure.services.refresh_token_service import RefreshTokenService
from infrastructure.services.register_service import RegisterService

from server.dependencies import get_session, get_redis, config

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_token_helper(redis: Redis = Depends(get_redis)) -> ITokenHelper:
    return JwtTokenHelper(
        redis,
        config.secret_key,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


def get_register_service(
    session: AsyncSession = Depends(get_session),
    hasher: PasswordHasher = Depends(get_password_hasher),
    token_helper: ITokenHelper = Depends(get_token_helper),
) -> RegisterService:
    return RegisterService(session, hasher, token_helper)


def get_login_service(
    session: AsyncSession = Depends(get_session),
    hasher: PasswordHasher = Depends(get_password_hasher),
    token_helper: ITokenHelper = Depends(get_token_helper),
) -> LoginService:
    return LoginService(session, hasher, token_helper)


def get_refresh_token_service(
    session: AsyncSession = Depends(get_session),
    token_helper: ITokenHelper = Depends(get_token_helper),
) -> RefreshTokenService:
    return RefreshTokenService(session, token_helper)


def get_logout_service(
    session: AsyncSession = Depends(get_session),
    token_helper: ITokenHelper = Depends(get_token_helper),
) -> LogoutService:
    return LogoutService(session, token_helper)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_helper: ITokenHelper = Depends(get_token_helper),
):
    try:
        payload = await token_helper.verify_access_token(credentials.credentials)
        return payload
    except AuthException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=TokenResponseDto)
async def register(
    body: RegisterDto,
    service: RegisterService = Depends(get_register_service),
) -> TokenResponseDto:
    """
    Регистрация нового пользователя

    - **login**: уникальный логин пользователя
    - **password**: пароль пользователя
    """
    return await service.execute(body)


@router.post("/login", response_model=TokenResponseDto)
async def login(
    body: LoginDto,
    service: LoginService = Depends(get_login_service),
) -> TokenResponseDto:
    """
    Вход в систему

    - **login**: логин пользователя
    - **password**: пароль пользователя
    """
    return await service.execute(body)


@router.post("/refresh", response_model=TokenResponseDto)
async def refresh_token(
    body: RefreshTokenDto,
    service: RefreshTokenService = Depends(get_refresh_token_service),
) -> TokenResponseDto:
    """
    Обновление access токена

    - **refresh_token**: токен для обновления доступа
    """
    return await service.execute(body)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: LogoutService = Depends(get_logout_service),
) -> None:
    """
    Выход из системы - отзывает текущий access токен
    """
    await service.execute(credentials.credentials)


@router.get("/me")
async def get_current_user_info(
    current_user=Depends(get_current_user),
):
    """
    Получить информацию о текущем пользователе
    """
    return {
        "user_id": current_user.user_id,
        "login": current_user.login,
        "exp": current_user.exp.isoformat(),
        "iat": current_user.iat.isoformat(),
    }