import jwt
from datetime import datetime, timedelta
from redis.asyncio import Redis

from domain.exceptions import TokenExpiredException, TokenInvalidException
from domain.model import TokenPair, TokenPayload
from infrastructure.interface.itoken_manager import ITokenManager


class JwtTokenHelper(ITokenManager):
    def __init__(
        self,
        redis_client: Redis,
        secret_key: str,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self.redis_client = redis_client
        self.secret_key = secret_key
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)
        self.algorithm = "HS256"

    async def create_tokens(self, user_id: int, login: str) -> TokenPair:
        now = datetime.utcnow()

        access_payload = {
            "user_id": user_id,
            "login": login,
            "exp": now + self.access_token_expire,
            "iat": now,
            "type": "access",
        }

        refresh_payload = {
            "user_id": user_id,
            "login": login,
            "exp": now + self.refresh_token_expire,
            "iat": now,
            "type": "refresh",
        }

        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(
            refresh_payload, self.secret_key, algorithm=self.algorithm
        )

        await self.redis_client.set(
            f"access_token:{access_token}",
            "active",
            ex=int(self.access_token_expire.total_seconds()),
        )

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def verify_access_token(self, token: str) -> TokenPayload:
        return await self._verify_token(token, "access")

    async def verify_refresh_token(self, token: str) -> TokenPayload:
        return await self._verify_token(token, "refresh")

    async def _verify_token(self, token: str, token_type: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenInvalidException(f"Invalid token: {str(e)}")

        if payload.get("type") != token_type:
            raise TokenInvalidException(f"Invalid token type. Expected {token_type}")

        if token_type == "access":
            is_revoked = await self.is_token_revoked(token)
            if is_revoked:
                raise TokenInvalidException("Token has been revoked")

        return TokenPayload(
            user_id=payload["user_id"],
            login=payload["login"],
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
        )

    async def revoke_access_token(self, token: str) -> None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload["exp"]
            
            ttl = int(exp - datetime.utcnow().timestamp())
            if ttl > 0:
                await self.redis_client.set(f"revoked_token:{token}", "revoked", ex=ttl)
        except jwt.InvalidTokenError:
            pass

    async def is_token_revoked(self, token: str) -> bool:
        revoked = await self.redis_client.get(f"revoked_token:{token}")
        return revoked is not None