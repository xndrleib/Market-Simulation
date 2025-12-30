# Architecture

## Purpose
This project simulates a simple limit order book market with heterogeneous agents (noise traders, market makers, proprietary traders, and illegal strategies). The implementation is now separated into small modules to make the simulation easier to test, extend, and reuse.

## Module layout

- `src/market_simulation/types.py`
  - Shared dataclasses for orders, order requests, and trades.
- `src/market_simulation/order_book.py`
  - Price-time-priority limit order book and matching logic.
- `src/market_simulation/agents/`
  - Agent implementations split by strategy.
- `src/market_simulation/config.py`
  - Configuration dataclasses and random scenario sampling.
- `src/market_simulation/simulation.py`
  - Core simulation loop and result container.
- `src/market_simulation/features.py`
  - Feature extraction for agent-level and window-level datasets.
- `src/market_simulation/dataset.py`
  - Dataset generation across many runs with tqdm progress reporting.
- `src/market_simulation/plotting.py`
  - Plotting utilities for inspection and demos.
- `src/market_simulation/logging_utils.py`
  - Logging helpers for structured progress output.

## Design notes

- **Reproducibility**: each simulation uses a dedicated seed; dataset generation samples configs with a base seed to ensure deterministic outputs.
- **Observability**: dataset generation logs start/end summaries and exposes a tqdm progress bar for long runs.
- **Extensibility**: new agents can be added by subclassing `Agent` and returning `OrderRequest` objects.

## Inputs / outputs

- Inputs: `SimulationConfig` objects or randomized configs via `sample_random_config`.
- Outputs: `SimulationResult` with price series, agent states, and trade history.
- Derived outputs: per-agent and per-window feature DataFrames from `features.py`.
