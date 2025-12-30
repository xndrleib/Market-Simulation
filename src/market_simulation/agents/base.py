"""Base agent classes."""

from __future__ import annotations

import random
from typing import Optional

import numpy as np

from ..order_book import OrderBook
from ..types import OrderRequest


class Agent:
    """Base class for all agents.

    Parameters
    ----------
    agent_id
        Unique identifier.
    agent_type
        Label describing the agent category.
    rng
        Python RNG for discrete draws.
    np_rng
        NumPy RNG for continuous draws.
    """

    def __init__(
        self,
        agent_id: int,
        agent_type: str,
        rng: random.Random,
        np_rng: np.random.Generator,
    ) -> None:
        self.id = agent_id
        self.type = agent_type
        self.rng = rng
        self.np_rng = np_rng
        self.cash = 0.0
        self.position = 0
        self.trade_history: list[dict[str, float | int | str]] = []

        self.label_is_illegal: bool = False
        self.label_illegal_type: Optional[str] = None
        self.group_id: Optional[int] = None

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        """Return a list of order requests for this time step."""

        return []

    def on_trade(self, price: float, quantity: int, side: str) -> None:
        """Update cash and position when a trade executes."""

        if side == "BUY":
            self.position += quantity
            self.cash -= price * quantity
        else:
            self.position -= quantity
            self.cash += price * quantity

        self.trade_history.append(
            {"price": price, "quantity": quantity, "side": side}
        )
