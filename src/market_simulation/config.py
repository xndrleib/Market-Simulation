"""Simulation configuration and sampling utilities."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InsiderSpec:
    """Configuration for a single illegal agent in a scenario.

    Parameters
    ----------
    strategy
        Strategy label ("event", "slow", "stealth", "ring", or "pump").
    start_time
        Optional start time for strategies that require it.
    trade_size
        Optional trade size override.
    group_id
        Optional group identifier for coordinated agents.
    """

    strategy: str
    start_time: Optional[int] = None
    trade_size: Optional[int] = None
    group_id: Optional[int] = None


@dataclass
class SimulationConfig:
    """Configuration for a single simulation run."""

    run_id: int
    T: int = 1000
    has_event: bool = True
    event_time: Optional[int] = None
    jump_size: float = 0.1
    jump_direction: int = 1
    volatility: float = 0.05
    n_noise_traders: int = 20
    n_market_makers: int = 1
    n_prop_traders: int = 0
    insider_specs: list[InsiderSpec] = field(default_factory=list)
    seed: Optional[int] = None


def sample_random_config(run_id: int, rng: Optional[random.Random] = None) -> SimulationConfig:
    """Sample a random scenario configuration.

    Parameters
    ----------
    run_id
        Identifier for the run.
    rng
        Optional random number generator used for reproducible sampling. If ``None``,
        a new generator is created using ``run_id`` as the seed.
    """

    if rng is None:
        rng = random.Random(run_id)

    T = rng.randint(800, 1500)

    has_event = rng.random() < 0.7
    if has_event:
        event_time = rng.randint(int(0.3 * T), int(0.8 * T))
        jump_size = rng.uniform(0.05, 0.2)
        jump_direction = rng.choice([-1, 1])
    else:
        event_time = None
        jump_size = 0.0
        jump_direction = 0

    n_noise_traders = rng.randint(10, 40)
    n_market_makers = rng.choice([1, 2])
    n_prop_traders = rng.choice([0, 1, 2])

    insider_specs: list[InsiderSpec] = []

    if has_event:
        if rng.random() < 0.7:
            n_insiders = rng.randint(1, 3)
            if rng.random() < 0.4 and n_insiders >= 2:
                group_id = rng.randint(1, 10_000)
                for _ in range(n_insiders):
                    insider_specs.append(InsiderSpec(strategy="ring", group_id=group_id))
            else:
                for _ in range(n_insiders):
                    strategy = rng.choice(["event", "slow", "stealth"])
                    insider_specs.append(InsiderSpec(strategy=strategy))
    else:
        if rng.random() < 0.3:
            n_illegal = rng.randint(1, 2)
            group_id = rng.randint(1, 10_000) if n_illegal > 1 else None
            for _ in range(n_illegal):
                insider_specs.append(InsiderSpec(strategy="pump", group_id=group_id))

    seed = rng.randint(0, 2**31 - 1)

    return SimulationConfig(
        run_id=run_id,
        T=T,
        has_event=has_event,
        event_time=event_time,
        jump_size=jump_size,
        jump_direction=jump_direction,
        volatility=0.05,
        n_noise_traders=n_noise_traders,
        n_market_makers=n_market_makers,
        n_prop_traders=n_prop_traders,
        insider_specs=insider_specs,
        seed=seed,
    )
