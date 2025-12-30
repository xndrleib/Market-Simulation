"""Simulation engine."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from .agents import (
    EventInsider,
    MarketMaker,
    NoiseTrader,
    PropTrader,
    PumpAndDumpManipulator,
    SlowInsider,
    StealthInsider,
)
from .config import SimulationConfig
from .logging_utils import log_kv
from .order_book import OrderBook
from .types import Order, OrderRequest, Trade


@dataclass
class SimulationResult:
    """Outputs of a simulation run."""

    config: SimulationConfig
    fundamental_values: np.ndarray
    mid_prices: np.ndarray
    book: OrderBook
    agents: list
    trades: list[Trade]

    def trades_frame(self) -> pd.DataFrame:
        """Return a pandas DataFrame of trades."""

        if not self.trades:
            return pd.DataFrame(columns=["time", "price", "quantity", "buy_agent", "sell_agent"])
        return pd.DataFrame([trade.as_dict() for trade in self.trades])


def _make_rng(seed: Optional[int], fallback: int) -> tuple[random.Random, np.random.Generator]:
    seed_value = fallback if seed is None else seed
    return random.Random(seed_value), np.random.default_rng(seed_value)


def _spawn_agent_rng(py_rng: random.Random) -> tuple[random.Random, np.random.Generator]:
    seed = py_rng.randint(0, 2**31 - 1)
    return random.Random(seed), np.random.default_rng(seed)


def _build_agents(config: SimulationConfig, py_rng: random.Random) -> list:
    agents: list = []
    next_agent_id = 1

    for _ in range(config.n_market_makers):
        agent_rng, agent_np_rng = _spawn_agent_rng(py_rng)
        spread = py_rng.uniform(0.0015, 0.003)
        size = py_rng.randint(10, 30)
        max_inv = py_rng.randint(150, 300)
        agents.append(
            MarketMaker(
                agent_id=next_agent_id,
                spread=spread,
                size=size,
                max_inventory=max_inv,
                rng=agent_rng,
                np_rng=agent_np_rng,
            )
        )
        next_agent_id += 1

    for _ in range(config.n_prop_traders):
        agent_rng, agent_np_rng = _spawn_agent_rng(py_rng)
        mode = py_rng.choice(["momentum", "mean_reversion"])
        p_trade = py_rng.uniform(0.2, 0.4)
        max_qty = py_rng.randint(5, 20)
        agents.append(
            PropTrader(
                agent_id=next_agent_id,
                mode=mode,
                p_trade=p_trade,
                max_qty=max_qty,
                rng=agent_rng,
                np_rng=agent_np_rng,
            )
        )
        next_agent_id += 1

    for _ in range(config.n_noise_traders):
        agent_rng, agent_np_rng = _spawn_agent_rng(py_rng)
        p_trade = py_rng.uniform(0.1, 0.4)
        p_market = py_rng.uniform(0.2, 0.8)
        max_qty = py_rng.randint(5, 20)
        direction_bias = py_rng.uniform(-0.1, 0.1)
        agents.append(
            NoiseTrader(
                agent_id=next_agent_id,
                p_trade=p_trade,
                p_market=p_market,
                max_qty=max_qty,
                direction_bias=direction_bias,
                rng=agent_rng,
                np_rng=agent_np_rng,
            )
        )
        next_agent_id += 1

    for spec in config.insider_specs:
        strat = spec.strategy
        group_id = spec.group_id

        if strat in ("event", "ring", "slow", "stealth"):
            if not config.has_event or config.event_time is None or config.jump_direction == 0:
                continue

            agent_rng, agent_np_rng = _spawn_agent_rng(py_rng)
            event_time = config.event_time
            direction = config.jump_direction

            if strat in ("event", "ring"):
                start_time = event_time - py_rng.randint(40, 100)
                trade_size = spec.trade_size if spec.trade_size is not None else py_rng.randint(6, 12)
                unwind_horizon = py_rng.randint(60, 120)
                insider = EventInsider(
                    agent_id=next_agent_id,
                    event_time=event_time,
                    direction=direction,
                    start_time=start_time,
                    trade_size=trade_size,
                    unwind_horizon=unwind_horizon,
                    group_id=group_id,
                    rng=agent_rng,
                    np_rng=agent_np_rng,
                )
            elif strat == "slow":
                start_time = event_time - py_rng.randint(150, 350)
                max_trade_size = spec.trade_size if spec.trade_size is not None else py_rng.randint(3, 7)
                p_trade_pre = py_rng.uniform(0.2, 0.4)
                unwind_horizon = py_rng.randint(100, 160)
                insider = SlowInsider(
                    agent_id=next_agent_id,
                    event_time=event_time,
                    direction=direction,
                    start_time=start_time,
                    max_trade_size=max_trade_size,
                    p_trade_pre=p_trade_pre,
                    unwind_horizon=unwind_horizon,
                    rng=agent_rng,
                    np_rng=agent_np_rng,
                )
            else:
                start_time = event_time - py_rng.randint(80, 160)
                max_trade_size = spec.trade_size if spec.trade_size is not None else py_rng.randint(4, 10)
                p_trade_pre = py_rng.uniform(0.3, 0.5)
                decoy_prob = py_rng.uniform(0.1, 0.25)
                unwind_horizon = py_rng.randint(60, 120)
                insider = StealthInsider(
                    agent_id=next_agent_id,
                    event_time=event_time,
                    direction=direction,
                    start_time=start_time,
                    max_trade_size=max_trade_size,
                    p_trade_pre=p_trade_pre,
                    decoy_prob=decoy_prob,
                    unwind_horizon=unwind_horizon,
                    rng=agent_rng,
                    np_rng=agent_np_rng,
                )

        elif strat == "pump":
            agent_rng, agent_np_rng = _spawn_agent_rng(py_rng)
            start_time = spec.start_time
            if start_time is None:
                start_time = py_rng.randint(int(0.2 * config.T), int(0.6 * config.T))
            direction = py_rng.choice([1, -1])
            pump_horizon = py_rng.randint(40, 100)
            unwind_horizon = py_rng.randint(40, 120)
            trade_size = spec.trade_size if spec.trade_size is not None else py_rng.randint(8, 15)
            insider = PumpAndDumpManipulator(
                agent_id=next_agent_id,
                start_time=start_time,
                direction=direction,
                pump_horizon=pump_horizon,
                unwind_horizon=unwind_horizon,
                trade_size=trade_size,
                group_id=group_id,
                rng=agent_rng,
                np_rng=agent_np_rng,
            )
        else:
            continue

        agents.append(insider)
        next_agent_id += 1

    return agents


def _orders_from_requests(
    requests: list[OrderRequest],
    order_id_counter: int,
    t: int,
    agent_id: int,
) -> tuple[list[Order], int]:
    orders: list[Order] = []
    current_id = order_id_counter
    for req in requests:
        order = Order(
            id=current_id,
            time=t,
            agent_id=agent_id,
            side=req.side,
            price=req.price,
            quantity=req.quantity,
            is_market=req.is_market,
        )
        orders.append(order)
        current_id += 1
    return orders, current_id


def run_simulation(
    config: SimulationConfig,
    logger: Optional[logging.Logger] = None,
) -> SimulationResult:
    """Run a single simulation.

    Parameters
    ----------
    config
        Simulation configuration.
    logger
        Optional logger for progress messages.
    """

    py_rng, np_rng = _make_rng(config.seed, config.run_id)

    book = OrderBook()
    agents = _build_agents(config, py_rng)
    agents_by_id = {agent.id: agent for agent in agents}

    fundamental_values: list[float] = []
    mid_prices: list[float] = []
    v = 100.0

    order_id_counter = 1

    for t in range(config.T):
        if (
            config.has_event
            and config.event_time is not None
            and config.jump_direction != 0
            and t == config.event_time
        ):
            v *= 1 + config.jump_direction * abs(config.jump_size)
        else:
            v += float(np_rng.normal(0, config.volatility))

        fundamental_values.append(v)

        mid_before = book.mid_price(v)

        for agent in agents:
            order_requests = agent.step(t, book, v, mid_before)
            orders, order_id_counter = _orders_from_requests(
                order_requests,
                order_id_counter,
                t,
                agent.id,
            )
            for order in orders:
                trades = book.process_order(order)
                for trade in trades:
                    buy_agent = agents_by_id[trade.buy_agent]
                    sell_agent = agents_by_id[trade.sell_agent]
                    buy_agent.on_trade(trade.price, trade.quantity, "BUY")
                    sell_agent.on_trade(trade.price, trade.quantity, "SELL")

        mid_after = book.mid_price(v)
        mid_prices.append(mid_after)

    if logger is not None:
        log_kv(
            logger,
            "simulation_completed",
            run_id=config.run_id,
            steps=config.T,
            trades=len(book.trades),
            agents=len(agents),
        )

    return SimulationResult(
        config=config,
        fundamental_values=np.array(fundamental_values),
        mid_prices=np.array(mid_prices),
        book=book,
        agents=agents,
        trades=book.trades,
    )
