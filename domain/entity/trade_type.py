from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel, Str128


class TradeType(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True, nullable=False)
    trades: Mapped[list["Trade"]] = relationship(back_populates="trade_type")
