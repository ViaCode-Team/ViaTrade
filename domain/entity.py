from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
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


class TradeType(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    trades: Mapped[list["Trade"]] = relationship(back_populates="trade_type")


class TradeCode(BaseModel):
    exchange_id: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    description: Mapped[Str512 | None]

    trades: Mapped[list["Trade"]] = relationship(back_populates="trade_code")
    user_trade_codes: Mapped[list["UserTradeCode"]] = relationship(back_populates="trade_code")


class Trade(BaseModel):
    date_open: Mapped[datetime]
    date_close: Mapped[datetime | None]
    trade_open: Mapped[float]
    trade_close: Mapped[float | None]
    net_income: Mapped[float | None]
    count: Mapped[int]

    trade_type_id: Mapped[int] = mapped_column(ForeignKey("tradetypes.id"))
    trade_code_id: Mapped[int] = mapped_column(ForeignKey("tradecodes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    trade_type: Mapped["TradeType"] = relationship(back_populates="trades")
    trade_code: Mapped["TradeCode"] = relationship(back_populates="trades")
    user: Mapped["User"] = relationship(back_populates="trades")


class UserTradeCode(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trade_code_id: Mapped[int] = mapped_column(ForeignKey("tradecodes.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "trade_code_id", name="uq_user_trade_code"),
    )

    user: Mapped["User"] = relationship(back_populates="user_trade_codes")
    trade_code: Mapped["TradeCode"] = relationship(back_populates="user_trade_codes")


class TradeStrategy(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    description: Mapped[Str512 | None]

    user_trade_strategies: Mapped[list["UserTradeStrategy"]] = relationship(back_populates="trade_strategy")


class UserTradeStrategy(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trade_strategy_id: Mapped[int] = mapped_column(ForeignKey("tradestrategies.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "trade_strategy_id", name="uq_user_trade_strategy"),
    )

    user: Mapped["User"] = relationship(back_populates="user_trade_strategies")
    trade_strategy: Mapped["TradeStrategy"] = relationship(back_populates="user_trade_strategies")
