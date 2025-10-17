from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, Str128, Str512


class User(BaseModel):
    login: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    hash_password: Mapped[Str512]
    last_login_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    refresh_token: Mapped[Str512 | None]

    trades: Mapped[list["Trade"]] = relationship(back_populates="user")
    user_trade_codes: Mapped[list["UserTradeCode"]] = relationship(back_populates="user")
    user_trade_strategies: Mapped[list["UserTradeStrategy"]] = relationship(back_populates="user")
    