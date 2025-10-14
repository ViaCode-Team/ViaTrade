from abc import ABC, abstractmethod

from domain.model import TokenPair, TokenPayload


class ITokenManager(ABC):
    @abstractmethod
    async def create_tokens(self, user_id: int, login: str) -> TokenPair:
        pass

    @abstractmethod
    async def verify_access_token(self, token: str) -> TokenPayload:
        pass

    @abstractmethod
    async def verify_refresh_token(self, token: str) -> TokenPayload:
        pass

    @abstractmethod
    async def revoke_access_token(self, token: str) -> None:
        pass

    @abstractmethod
    async def is_token_revoked(self, token: str) -> bool:
        pass