"""Feature extraction utilities."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .agents.base import Agent
from .config import SimulationConfig


def build_agent_trade_table(trades_df: pd.DataFrame) -> pd.DataFrame:
    """Expand trade records into per-agent trade entries.

    Parameters
    ----------
    trades_df
        DataFrame of trades with columns: time, price, quantity, buy_agent, sell_agent.
    """

    if trades_df is None or trades_df.empty:
        return pd.DataFrame(columns=["time", "agent_id", "side", "quantity", "price"])

    rows: list[dict[str, Any]] = []
    for _, tr in trades_df.iterrows():
        rows.append(
            {
                "time": int(tr["time"]),
                "agent_id": int(tr["buy_agent"]),
                "side": "BUY",
                "quantity": float(tr["quantity"]),
                "price": float(tr["price"]),
            }
        )
        rows.append(
            {
                "time": int(tr["time"]),
                "agent_id": int(tr["sell_agent"]),
                "side": "SELL",
                "quantity": float(tr["quantity"]),
                "price": float(tr["price"]),
            }
        )

    return pd.DataFrame(rows)


def extract_agent_features(
    run_id: int,
    agents: list[Agent],
    trades_df: pd.DataFrame,
    config: SimulationConfig,
    mid_prices: np.ndarray,
) -> pd.DataFrame:
    """Compute per-agent summary features.

    Parameters
    ----------
    run_id
        Simulation run identifier.
    agents
        Agent instances.
    trades_df
        Trade DataFrame.
    config
        Simulation configuration.
    mid_prices
        Array of mid prices.
    """

    agent_trade_df = build_agent_trade_table(trades_df)
    agent_trade_df["run_id"] = run_id

    event_time = config.event_time if config.has_event else None
    event_direction = config.jump_direction if config.has_event else 0

    rows: list[dict[str, Any]] = []
    last_mid = float(mid_prices[-1]) if len(mid_prices) > 0 else 100.0

    for agent in agents:
        at = agent_trade_df[agent_trade_df["agent_id"] == agent.id]

        n_trades = len(at)
        total_volume = float(at["quantity"].sum()) if n_trades > 0 else 0.0

        if n_trades > 0:
            signed = np.where(at["side"] == "BUY", at["quantity"], -at["quantity"])
            net_volume = float(signed.sum())
        else:
            net_volume = 0.0

        if event_time is not None:
            pre = at[at["time"] < event_time]
            post = at[at["time"] >= event_time]
            pre_vol = float(pre["quantity"].sum())
            post_vol = float(post["quantity"].sum())

            if event_direction != 0 and len(pre) > 0:
                pre_signed = np.where(pre["side"] == "BUY", pre["quantity"], -pre["quantity"])
                aligned = pre_signed if event_direction > 0 else -pre_signed
                aligned_pre_vol = float(aligned[aligned > 0].sum())
            else:
                aligned_pre_vol = 0.0
        else:
            pre_vol = post_vol = aligned_pre_vol = 0.0

        avg_trade_size = float(at["quantity"].mean()) if n_trades > 0 else 0.0
        buy_vol = float(at.loc[at["side"] == "BUY", "quantity"].sum()) if n_trades > 0 else 0.0
        sell_vol = float(at.loc[at["side"] == "SELL", "quantity"].sum()) if n_trades > 0 else 0.0

        equity = agent.cash + agent.position * last_mid

        rows.append(
            {
                "run_id": run_id,
                "agent_id": agent.id,
                "type": agent.type,
                "label_is_illegal": agent.label_is_illegal,
                "label_illegal_type": agent.label_illegal_type,
                "group_id": agent.group_id,
                "cash_final": float(agent.cash),
                "position_final": int(agent.position),
                "equity_final": float(equity),
                "n_trades": int(n_trades),
                "total_volume": total_volume,
                "net_volume": net_volume,
                "avg_trade_size": avg_trade_size,
                "buy_volume": buy_vol,
                "sell_volume": sell_vol,
                "pre_event_volume": pre_vol,
                "post_event_volume": post_vol,
                "aligned_pre_event_volume": aligned_pre_vol,
            }
        )

    return pd.DataFrame(rows)


def extract_window_features(
    run_id: int,
    agents: list[Agent],
    trades_df: pd.DataFrame,
    config: SimulationConfig,
    mid_prices: np.ndarray,
    window_size: int = 50,
) -> pd.DataFrame:
    """Compute sequential window-level features and labels.

    Parameters
    ----------
    run_id
        Simulation run identifier.
    agents
        Agent instances.
    trades_df
        Trade DataFrame.
    config
        Simulation configuration.
    mid_prices
        Mid price series.
    window_size
        Size of each non-overlapping window.
    """

    if len(mid_prices) == 0:
        return pd.DataFrame()

    illegal_ids = {agent.id for agent in agents if agent.label_is_illegal}

    if trades_df is None:
        trades_df = pd.DataFrame(columns=["time", "quantity", "buy_agent", "sell_agent"])

    agent_trades = build_agent_trade_table(trades_df)

    T = len(mid_prices)
    returns = np.diff(np.log(mid_prices + 1e-8))

    rows: list[dict[str, Any]] = []
    event_time = config.event_time if config.has_event else None
    n_windows = T // window_size

    for w in range(n_windows):
        start = w * window_size
        end = start + window_size

        mask_trades = (trades_df["time"] >= start) & (trades_df["time"] < end)
        w_trades = trades_df[mask_trades]

        mask_agent_trades = (agent_trades["time"] >= start) & (agent_trades["time"] < end)
        w_agent_trades = agent_trades[mask_agent_trades]

        total_vol = float(w_trades["quantity"].sum()) if not w_trades.empty else 0.0
        n_trades = int(len(w_trades))

        agents_in_window = set(w_agent_trades["agent_id"]) if not w_agent_trades.empty else set()
        has_illegal = int(len(agents_in_window.intersection(illegal_ids)) > 0)

        if not w_agent_trades.empty:
            buy_vol = float(w_agent_trades.loc[w_agent_trades["side"] == "BUY", "quantity"].sum())
            sell_vol = float(w_agent_trades.loc[w_agent_trades["side"] == "SELL", "quantity"].sum())
        else:
            buy_vol = 0.0
            sell_vol = 0.0

        if end < len(mid_prices):
            w_rets = returns[start : end - 1]
        else:
            w_rets = returns[start:]
        vol = float(np.std(w_rets)) if len(w_rets) > 0 else 0.0

        if event_time is not None:
            center = (start + end) / 2
            event_distance = float(center - event_time)
        else:
            event_distance = 0.0

        rows.append(
            {
                "run_id": run_id,
                "window_index": w,
                "start_time": start,
                "end_time": end,
                "n_trades": n_trades,
                "total_volume": total_vol,
                "buy_volume": buy_vol,
                "sell_volume": sell_vol,
                "n_active_agents": int(len(agents_in_window)),
                "realized_volatility": vol,
                "has_illegal_activity": has_illegal,
                "event_distance": event_distance,
            }
        )

    return pd.DataFrame(rows)
