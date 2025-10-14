from dataclasses import dataclass


@dataclass
class RegisterDto:
    login: str
    password: str


@dataclass
class LoginDto:
    login: str
    password: str


@dataclass
class TokenResponseDto:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class RefreshTokenDto:
    refresh_token: str
