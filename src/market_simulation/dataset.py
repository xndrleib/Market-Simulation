"""Dataset generation utilities."""

from __future__ import annotations

import logging
import random
from typing import Optional

import pandas as pd
from tqdm.auto import tqdm

from .config import sample_random_config
from .features import extract_agent_features, extract_window_features
from .logging_utils import log_kv
from .simulation import run_simulation


def generate_dataset(
    n_runs: int = 20,
    window_size: int = 50,
    base_seed: int = 42,
    logger: Optional[logging.Logger] = None,
) -> dict[str, pd.DataFrame]:
    """Generate agent- and window-level datasets across multiple runs.

    Parameters
    ----------
    n_runs
        Number of simulation runs.
    window_size
        Window size for sequential features.
    base_seed
        Seed for reproducible configuration sampling.
    logger
        Optional logger for structured progress updates.
    """

    if logger is not None:
        log_kv(logger, "dataset_generation_started", n_runs=n_runs, window_size=window_size)

    agent_rows_all: list[pd.DataFrame] = []
    window_rows_all: list[pd.DataFrame] = []

    rng = random.Random(base_seed)

    for run_id in tqdm(range(n_runs), desc="Simulations"):
        config = sample_random_config(run_id=run_id, rng=rng)
        results = run_simulation(config, logger=logger)

        trades_df = results.trades_frame()

        agent_df = extract_agent_features(
            run_id=run_id,
            agents=results.agents,
            trades_df=trades_df,
            config=config,
            mid_prices=results.mid_prices,
        )
        window_df = extract_window_features(
            run_id=run_id,
            agents=results.agents,
            trades_df=trades_df,
            config=config,
            mid_prices=results.mid_prices,
            window_size=window_size,
        )

        agent_rows_all.append(agent_df)
        window_rows_all.append(window_df)

    agent_frames = [df for df in agent_rows_all if df is not None and not df.empty]
    window_frames = [df for df in window_rows_all if df is not None and not df.empty]

    agent_level = pd.concat(agent_frames, ignore_index=True) if agent_frames else pd.DataFrame()
    window_level = pd.concat(window_frames, ignore_index=True) if window_frames else pd.DataFrame()

    if logger is not None:
        log_kv(
            logger,
            "dataset_generation_completed",
            agent_rows=len(agent_level),
            window_rows=len(window_level),
        )

    return {"agent_level": agent_level, "window_level": window_level}
