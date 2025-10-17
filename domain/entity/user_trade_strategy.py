from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class UserTradeStrategy(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trade_strategy_id: Mapped[int] = mapped_column(ForeignKey("tradestrategys.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "trade_strategy_id", name="uq_user_trade_strategy"),
    )

    user: Mapped["User"] = relationship(back_populates="user_trade_strategies")
    trade_strategy: Mapped["TradeStrategy"] = relationship(back_populates="user_trade_strategies")
