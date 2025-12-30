"""Prop trader agent."""

from __future__ import annotations

from typing import Optional

from ..order_book import OrderBook
from ..types import OrderRequest
from .base import Agent


class PropTrader(Agent):
    """Momentum or mean-reversion prop trader."""

    def __init__(
        self,
        agent_id: int,
        mode: str,
        p_trade: float,
        max_qty: int,
        rng,
        np_rng,
    ) -> None:
        super().__init__(agent_id, agent_type="PROP", rng=rng, np_rng=np_rng)
        if mode not in ("momentum", "mean_reversion"):
            raise ValueError("mode must be 'momentum' or 'mean_reversion'")
        self.mode = mode
        self.p_trade = p_trade
        self.max_qty = max_qty
        self.last_mid: Optional[float] = None

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        if self.last_mid is None:
            self.last_mid = mid_price
            return []

        if self.rng.random() > self.p_trade:
            self.last_mid = mid_price
            return []

        price_change = mid_price - self.last_mid
        if abs(price_change) < 1e-6:
            self.last_mid = mid_price
            return []

        if self.mode == "momentum":
            side = "BUY" if price_change > 0 else "SELL"
        else:
            side = "SELL" if price_change > 0 else "BUY"

        quantity = self.rng.randint(1, self.max_qty)
        is_market = self.rng.random() < 0.6

        if is_market:
            price = None
        else:
            price = mid_price * (0.999 if side == "BUY" else 1.001)
            price = round(float(price), 2)

        self.last_mid = mid_price

        return [
            OrderRequest(
                side=side,
                quantity=quantity,
                price=price,
                is_market=is_market,
            )
        ]
