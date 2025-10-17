from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class UserTradeCode(BaseModel):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trade_code_id: Mapped[int] = mapped_column(ForeignKey("tradecodes.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "trade_code_id", name="uq_user_trade_code"),
    )

    user: Mapped["User"] = relationship(back_populates="user_trade_codes")
    trade_code: Mapped["TradeCode"] = relationship(back_populates="user_trade_codes")
