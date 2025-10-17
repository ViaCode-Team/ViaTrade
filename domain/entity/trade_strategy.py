from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, Str128, Str512


class TradeStrategy(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    description: Mapped[Str512 | None]

    user_trade_strategies: Mapped[list["UserTradeStrategy"]] = relationship(back_populates="trade_strategy")
