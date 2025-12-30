"""Core shared types for the market simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

Side = Literal["BUY", "SELL"]


@dataclass
class Order:
    """Executable order submitted to the order book.

    Parameters
    ----------
    id
        Unique order identifier.
    time
        Simulation time step when the order is submitted.
    agent_id
        Identifier of the submitting agent.
    side
        "BUY" or "SELL".
    price
        Limit price for a limit order, or ``None`` for market orders.
    quantity
        Quantity to trade.
    is_market
        Whether the order is a market order.
    """

    id: int
    time: int
    agent_id: int
    side: Side
    price: Optional[float]
    quantity: int
    is_market: bool = False

    def __post_init__(self) -> None:
        if self.side not in ("BUY", "SELL"):
            raise ValueError(f"Invalid side: {self.side}")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.is_market:
            if self.price is not None:
                raise ValueError("Market orders must not specify price")
        else:
            if self.price is None:
                raise ValueError("Limit orders must specify price")
            if self.price <= 0:
                raise ValueError("Price must be positive")


@dataclass(frozen=True)
class OrderRequest:
    """Order request emitted by an agent.

    Parameters
    ----------
    side
        "BUY" or "SELL".
    quantity
        Quantity to trade.
    price
        Limit price for limit orders, or ``None`` for market orders.
    is_market
        Whether the order should be executed as a market order.
    """

    side: Side
    quantity: int
    price: Optional[float]
    is_market: bool

    def __post_init__(self) -> None:
        if self.side not in ("BUY", "SELL"):
            raise ValueError(f"Invalid side: {self.side}")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.is_market:
            if self.price is not None:
                raise ValueError("Market order request must not include a price")
        else:
            if self.price is None:
                raise ValueError("Limit order request must include a price")
            if self.price <= 0:
                raise ValueError("Price must be positive")


@dataclass(frozen=True)
class Trade:
    """Trade produced by matching an order.

    Parameters
    ----------
    time
        Simulation time step when the trade executes.
    price
        Execution price.
    quantity
        Executed quantity.
    buy_agent
        Buying agent identifier.
    sell_agent
        Selling agent identifier.
    """

    time: int
    price: float
    quantity: int
    buy_agent: int
    sell_agent: int

    def as_dict(self) -> dict[str, float | int]:
        """Return a dictionary representation of the trade."""

        return {
            "time": self.time,
            "price": self.price,
            "quantity": self.quantity,
            "buy_agent": self.buy_agent,
            "sell_agent": self.sell_agent,
        }
