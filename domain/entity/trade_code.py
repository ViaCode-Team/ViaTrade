from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, Str128, Str512


class TradeCode(BaseModel):
    exchange_id: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    description: Mapped[Str512 | None]

    trades: Mapped[list["Trade"]] = relationship(back_populates="trade_code")
    user_trade_codes: Mapped[list["UserTradeCode"]] = relationship(back_populates="trade_code")
