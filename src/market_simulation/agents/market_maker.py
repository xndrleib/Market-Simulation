"""Market maker agent."""

from __future__ import annotations

from ..order_book import OrderBook
from ..types import OrderRequest
from .base import Agent


class MarketMaker(Agent):
    """Simple inventory-skewed market maker."""

    def __init__(
        self,
        agent_id: int,
        spread: float,
        size: int,
        max_inventory: int,
        rng,
        np_rng,
    ) -> None:
        super().__init__(agent_id, agent_type="MM", rng=rng, np_rng=np_rng)
        self.spread = spread
        self.size = size
        self.max_inventory = max_inventory

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        book.cancel_agent_orders(self.id)

        inventory_skew = 0.001 * self.position
        bid_price = mid_price * (1 - self.spread - inventory_skew)
        ask_price = mid_price * (1 + self.spread - inventory_skew)

        bid_price = round(float(bid_price), 2)
        ask_price = round(float(ask_price), 2)

        orders: list[OrderRequest] = []

        if self.position < self.max_inventory:
            orders.append(
                OrderRequest(
                    side="BUY",
                    quantity=self.size,
                    price=bid_price,
                    is_market=False,
                )
            )
        if self.position > -self.max_inventory:
            orders.append(
                OrderRequest(
                    side="SELL",
                    quantity=self.size,
                    price=ask_price,
                    is_market=False,
                )
            )

        return orders
