"""Plotting helpers for simulation outputs."""

from __future__ import annotations

import logging
from typing import Optional

import matplotlib.pyplot as plt

from .features import build_agent_trade_table
from .logging_utils import log_kv
from .simulation import SimulationResult


def plot_price_with_insider_trades(
    results: SimulationResult,
    logger: Optional[logging.Logger] = None,
):
    """Plot mid price and fundamental value with insider trades.

    Parameters
    ----------
    results
        Simulation results.
    logger
        Optional logger for status messages.
    """

    logger = logger or logging.getLogger("market_simulation")

    config = results.config
    fundamental_values = results.fundamental_values
    mid_prices = results.mid_prices
    trades_df = results.trades_frame()
    agents = results.agents

    illegal_agents = [agent for agent in agents if agent.label_is_illegal]
    if not illegal_agents:
        log_kv(logger, "plot_skipped", reason="no_illegal_agents")
        return None, None

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(mid_prices, label="Mid price")
    ax.plot(fundamental_values, label="Fundamental value", linestyle="--", alpha=0.6)

    if config.has_event and config.event_time is not None:
        ax.axvline(config.event_time, color="k", linestyle=":", label="Event time")

    if trades_df.empty:
        ax.set_title("No trades to display")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.legend()
        fig.tight_layout()
        return fig, ax

    agent_trades = build_agent_trade_table(trades_df)

    for agent in illegal_agents:
        df_agent = agent_trades[agent_trades["agent_id"] == agent.id]
        if df_agent.empty:
            continue

        buys = df_agent[df_agent["side"] == "BUY"]
        sells = df_agent[df_agent["side"] == "SELL"]

        base_label = f"Agent {agent.id} ({agent.label_illegal_type})"
        if agent.group_id is not None:
            base_label += f" [group {agent.group_id}]"

        if not buys.empty:
            ax.scatter(
                buys["time"],
                buys["price"],
                marker="^",
                s=30,
                alpha=0.8,
                label=base_label + " buys",
            )
        if not sells.empty:
            ax.scatter(
                sells["time"],
                sells["price"],
                marker="v",
                s=30,
                alpha=0.8,
                label=base_label + " sells",
            )

    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.set_title("Price and insider/manipulator trades")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    return fig, ax


def plot_insider_positions(
    results: SimulationResult,
    logger: Optional[logging.Logger] = None,
):
    """Plot position time series for insider agents."""

    logger = logger or logging.getLogger("market_simulation")

    config = results.config
    agents = results.agents
    trades_df = results.trades_frame()
    mid_prices = results.mid_prices
    T = len(mid_prices)

    illegal_agents = [agent for agent in agents if agent.label_is_illegal]
    if not illegal_agents:
        log_kv(logger, "plot_skipped", reason="no_illegal_agents")
        return None, None

    if trades_df.empty:
        log_kv(logger, "plot_skipped", reason="no_trades")
        return None, None

    agent_trades = build_agent_trade_table(trades_df)

    fig, ax = plt.subplots(figsize=(10, 4))

    for agent in illegal_agents:
        df_agent = agent_trades[agent_trades["agent_id"] == agent.id].copy()
        if df_agent.empty:
            continue

        pos = [0.0] * T
        running_pos = 0.0

        trades_by_time = {int(t): grp for t, grp in df_agent.groupby("time")}

        for t in range(T):
            if t in trades_by_time:
                g = trades_by_time[t]
                signed = g["quantity"].where(g["side"] == "BUY", -g["quantity"])
                running_pos += float(signed.sum())
            pos[t] = running_pos

        label = f"Agent {agent.id} ({agent.label_illegal_type})"
        if agent.group_id is not None:
            label += f" [group {agent.group_id}]"
        ax.plot(pos, label=label)

    if config.has_event and config.event_time is not None:
        ax.axvline(config.event_time, color="k", linestyle=":", label="Event time")

    ax.set_xlabel("Time")
    ax.set_ylabel("Position")
    ax.set_title("Insider/manipulator positions over time")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    return fig, ax
