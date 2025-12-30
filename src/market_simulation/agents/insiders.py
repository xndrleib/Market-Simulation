"""Insider and manipulator agent strategies."""

from __future__ import annotations

from typing import Optional

from ..order_book import OrderBook
from ..types import OrderRequest
from .base import Agent


class InsiderBase(Agent):
    """Base class for illegal informational or manipulative strategies."""

    def __init__(
        self,
        agent_id: int,
        scenario_name: str,
        rng,
        np_rng,
        group_id: Optional[int] = None,
        event_time: Optional[int] = None,
        direction: int = 1,
    ) -> None:
        super().__init__(agent_id, agent_type="INSIDER", rng=rng, np_rng=np_rng)
        self.label_is_illegal = True
        self.label_illegal_type = scenario_name
        self.group_id = group_id
        self.event_time = event_time
        self.direction = direction


class EventInsider(InsiderBase):
    """Short-horizon event insider."""

    def __init__(
        self,
        agent_id: int,
        event_time: int,
        direction: int,
        start_time: Optional[int],
        trade_size: int,
        unwind_horizon: int,
        rng,
        np_rng,
        group_id: Optional[int] = None,
    ) -> None:
        super().__init__(
            agent_id,
            scenario_name="event_insider",
            group_id=group_id,
            event_time=event_time,
            direction=direction,
            rng=rng,
            np_rng=np_rng,
        )
        self.trade_size = trade_size
        self.unwind_horizon = unwind_horizon
        self.start_time = start_time if start_time is not None else max(0, event_time - 50)

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        if self.event_time is None or t < self.start_time:
            return []

        orders: list[OrderRequest] = []

        if self.start_time <= t < self.event_time:
            side = "BUY" if self.direction > 0 else "SELL"
            is_market = self.rng.random() < 0.3
            if is_market:
                price = None
            else:
                price = mid_price * (1.001 if side == "BUY" else 0.999)
                price = round(float(price), 2)

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=self.trade_size,
                    price=price,
                    is_market=is_market,
                )
            )

        elif self.event_time <= t < self.event_time + self.unwind_horizon:
            if self.direction > 0 and self.position > 0:
                side = "SELL"
                qty = min(self.trade_size, self.position)
            elif self.direction < 0 and self.position < 0:
                side = "BUY"
                qty = min(self.trade_size, abs(self.position))
            else:
                return []

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=qty,
                    price=None,
                    is_market=True,
                )
            )

        return orders


class SlowInsider(InsiderBase):
    """Slow accumulation insider."""

    def __init__(
        self,
        agent_id: int,
        event_time: int,
        direction: int,
        start_time: Optional[int],
        max_trade_size: int,
        p_trade_pre: float,
        unwind_horizon: int,
        rng,
        np_rng,
    ) -> None:
        super().__init__(
            agent_id,
            scenario_name="slow_insider",
            event_time=event_time,
            direction=direction,
            rng=rng,
            np_rng=np_rng,
        )
        self.max_trade_size = max_trade_size
        self.p_trade_pre = p_trade_pre
        self.unwind_horizon = unwind_horizon
        self.start_time = start_time if start_time is not None else max(0, event_time - 300)

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        if self.event_time is None or t < self.start_time:
            return []

        orders: list[OrderRequest] = []

        if self.start_time <= t < self.event_time:
            if self.rng.random() > self.p_trade_pre:
                return []
            side = "BUY" if self.direction > 0 else "SELL"
            quantity = self.rng.randint(1, self.max_trade_size)
            is_market = self.rng.random() < 0.1
            if is_market:
                price = None
            else:
                spread = 0.0015
                price = mid_price * (1 - spread if side == "BUY" else 1 + spread)
                price = round(float(price), 2)

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=quantity,
                    price=price,
                    is_market=is_market,
                )
            )

        elif self.event_time <= t < self.event_time + self.unwind_horizon:
            if self.direction > 0 and self.position > 0:
                side = "SELL"
                qty = min(self.max_trade_size, self.position)
            elif self.direction < 0 and self.position < 0:
                side = "BUY"
                qty = min(self.max_trade_size, abs(self.position))
            else:
                return []

            is_market = self.rng.random() < 0.5
            if is_market:
                price = None
            else:
                price = mid_price * (0.999 if side == "SELL" else 1.001)
                price = round(float(price), 2)

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=qty,
                    price=price,
                    is_market=is_market,
                )
            )

        return orders


class StealthInsider(InsiderBase):
    """Stealth insider with decoy trades."""

    def __init__(
        self,
        agent_id: int,
        event_time: int,
        direction: int,
        start_time: Optional[int],
        max_trade_size: int,
        p_trade_pre: float,
        decoy_prob: float,
        unwind_horizon: int,
        rng,
        np_rng,
    ) -> None:
        super().__init__(
            agent_id,
            scenario_name="stealth_insider",
            event_time=event_time,
            direction=direction,
            rng=rng,
            np_rng=np_rng,
        )
        self.max_trade_size = max_trade_size
        self.p_trade_pre = p_trade_pre
        self.decoy_prob = decoy_prob
        self.unwind_horizon = unwind_horizon
        self.start_time = start_time if start_time is not None else max(0, event_time - 120)

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        if self.event_time is None or t < self.start_time:
            return []

        orders: list[OrderRequest] = []

        if self.start_time <= t < self.event_time:
            if self.rng.random() > self.p_trade_pre:
                return []

            informed_side = "BUY" if self.direction > 0 else "SELL"
            is_decoy = self.rng.random() < self.decoy_prob
            if is_decoy:
                side = "SELL" if informed_side == "BUY" else "BUY"
            else:
                side = informed_side

            quantity = self.rng.randint(1, self.max_trade_size)
            is_market = self.rng.random() < 0.4

            if is_market:
                price = None
            else:
                offset = 0.002 if is_decoy else 0.001
                price = mid_price * (1 - offset if side == "BUY" else 1 + offset)
                price = round(float(price), 2)

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=quantity,
                    price=price,
                    is_market=is_market,
                )
            )

        elif self.event_time <= t < self.event_time + self.unwind_horizon:
            if self.direction > 0 and self.position > 0:
                side = "SELL"
                qty = min(self.max_trade_size, self.position)
            elif self.direction < 0 and self.position < 0:
                side = "BUY"
                qty = min(self.max_trade_size, abs(self.position))
            else:
                return []

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=qty,
                    price=None,
                    is_market=True,
                )
            )

        return orders


class PumpAndDumpManipulator(InsiderBase):
    """Pump-and-dump manipulator."""

    def __init__(
        self,
        agent_id: int,
        start_time: int,
        direction: int,
        pump_horizon: int,
        unwind_horizon: int,
        trade_size: int,
        rng,
        np_rng,
        group_id: Optional[int] = None,
    ) -> None:
        super().__init__(
            agent_id,
            scenario_name="pump_and_dump",
            group_id=group_id,
            event_time=None,
            direction=direction,
            rng=rng,
            np_rng=np_rng,
        )
        self.start_time = start_time
        self.pump_horizon = pump_horizon
        self.unwind_horizon = unwind_horizon
        self.trade_size = trade_size

    def step(
        self,
        t: int,
        book: OrderBook,
        fundamental: float,
        mid_price: float,
    ) -> list[OrderRequest]:
        if t < self.start_time:
            return []

        orders: list[OrderRequest] = []

        if self.start_time <= t < self.start_time + self.pump_horizon:
            side = "BUY" if self.direction > 0 else "SELL"
            is_market = self.rng.random() < 0.7
            if is_market:
                price = None
            else:
                price = mid_price * (1.002 if side == "BUY" else 0.998)
                price = round(float(price), 2)

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=self.trade_size,
                    price=price,
                    is_market=is_market,
                )
            )

        elif self.start_time + self.pump_horizon <= t < self.start_time + self.pump_horizon + self.unwind_horizon:
            if self.direction > 0 and self.position > 0:
                side = "SELL"
                qty = min(self.trade_size, self.position)
            elif self.direction < 0 and self.position < 0:
                side = "BUY"
                qty = min(self.trade_size, abs(self.position))
            else:
                return []

            orders.append(
                OrderRequest(
                    side=side,
                    quantity=qty,
                    price=None,
                    is_market=True,
                )
            )

        return orders
