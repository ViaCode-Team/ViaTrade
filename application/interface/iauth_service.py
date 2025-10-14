from abc import ABC, abstractmethod

from application.dto.auth_dto import LoginDto, TokenResponseDto


class IAuthService(ABC):
    @abstractmethod
    async def execute(self, dto: LoginDto) -> TokenResponseDto:
        pass