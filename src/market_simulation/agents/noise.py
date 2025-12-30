"""Noise trader agent."""

from __future__ import annotations

from ..order_book import OrderBook
from ..types import OrderRequest
from .base import Agent


class NoiseTrader(Agent):
    """Random liquidity-taking/providing agent."""

    def __init__(
        self,
        agent_id: int,
        p_trade: float,
        p_market: float,
        max_qty: int,
        direction_bias: float,
        rng,
        np_rng,
    ) -> None:
        super().__init__(agent_id, agent_type="NOISE", rng=rng, np_rng=np_rng)
        self.p_trade = p_trade
        self.p_market = p_market
        self.max_qty = max_qty
        self.direction_bias = direction_bias

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        if self.rng.random() > self.p_trade:
            return []

        base = self.rng.random() - 0.5 + self.direction_bias
        side = "BUY" if base >= 0 else "SELL"

        quantity = self.rng.randint(1, self.max_qty)
        is_market = self.rng.random() < self.p_market

        if is_market:
            price = None
        else:
            spread = 0.002
            noise = float(self.np_rng.normal(0, spread))
            if side == "BUY":
                price = mid_price * (1 - abs(noise))
            else:
                price = mid_price * (1 + abs(noise))
            price = round(float(price), 2)

        return [
            OrderRequest(
                side=side,
                quantity=quantity,
                price=price,
                is_market=is_market,
            )
        ]
