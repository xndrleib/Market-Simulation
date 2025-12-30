# Market Simulation

A toy limit order book market simulator with heterogeneous agents and feature extraction for downstream detection tasks (e.g., insider trading). The core logic is packaged under `src/market_simulation` with structured logging, reproducible configs, and tqdm-based progress reporting.

## Highlights

- Modular architecture: order book, agents, simulation loop, features, datasets, plotting.
- Reproducible runs via explicit seeds and deterministic config sampling.
- Structured logging to console + file and progress bars for long runs.
- Feature extraction for agent-level and window-level datasets.

## Repository layout

- `src/market_simulation/` - Python package implementation.
- `docs/architecture.md` - Design overview and module roles.
- `docs/usage.md` - Usage patterns and examples.
- `market-simulation.ipynb` - notebook demo.
- `tests/` - pytest-based unit tests.

### Dependencies

Core modules require:

- numpy
- pandas
- matplotlib
- tqdm

The ML demo cells in the notebooks additionally use:

- scikit-learn

## Quickstart

```python
from src.market_simulation import SimulationConfig, configure_logging, run_simulation

logger = configure_logging(run_id=0)
config = SimulationConfig(run_id=0, seed=123)
result = run_simulation(config, logger=logger)

print(result.trades_frame().head())
```

## Dataset generation

```python
from src.market_simulation import configure_logging, generate_dataset

logger = configure_logging()
frames = generate_dataset(n_runs=50, window_size=50, base_seed=123, logger=logger)

agent_df = frames["agent_level"]
window_df = frames["window_level"]
```

## Plotting

```python
from src.market_simulation import run_simulation, sample_random_config
from src.market_simulation.plotting import plot_insider_positions, plot_price_with_insider_trades

config = sample_random_config(run_id=1)
result = run_simulation(config)

plot_price_with_insider_trades(result)
plot_insider_positions(result)
```

## Reproducibility

- `SimulationConfig.seed` controls simulation determinism.
- `sample_random_config(run_id=...)` uses `run_id` as a default seed if no RNG is provided.
- Dataset generation is deterministic with a fixed `base_seed`.

## Logging and progress

- Use `configure_logging(...)` to enable structured console + file logs.
- Long-running dataset generation uses tqdm progress bars.
- Avoid `print` for status updates; use the logger instead.

## Tests

```bash
pytest -q
```

## Notebooks

Open either notebook for an end-to-end demo:

```bash
jupyter notebook market-simulation.ipynb
```

The notebooks are wired to the package modules. If imports fail, ensure `PYTHONPATH` includes `src/`.

## Notes

For deeper design details, see `docs/architecture.md` and `docs/usage.md`.

## Roadmap (theoretical improvements)

- **Market microstructure realism**
  - Add queue depth, cancellations, and explicit time priority.
  - Support discrete price grids and variable tick sizes.
- **Agent modeling**
  - Replace fixed heuristics with configurable policy classes (inventory-aware MM, adaptive noise, RL/behavioral props).
  - Add heterogeneity in risk aversion, order size distributions, and information arrival.
- **Event and information dynamics**
  - Model multi-stage news (rumor → confirmation → drift) and private/public diffusion.
  - Add uncertainty over event size/direction and allow insiders to infer/adapt.
- **Price formation & fundamentals**
  - Introduce regime switching, mean reversion, stochastic volatility, and fat-tail jumps.
  - Calibrate parameters to stylized facts (volatility clustering, spread dynamics).
- **Market impact & feedback**
  - Add temporary/permanent impact tied to order flow and depth.
  - Model reflexive agents that respond to their own impact.
- **Labels & detection targets**
  - Move from binary labels to multi-label taxonomy (information-based, manipulation, collusion).
  - Add causal labels (who moved price, who profited) and intent proxies.
- **Feature space**
  - Add order-flow imbalance, signed volume, Kyle’s lambda proxies, VPIN-like measures.
  - Add sequence features (windowed time series, embeddings) and event-aligned features.
- **Evaluation & validation**
  - Add baselines and adversarial “benign but suspicious” agents.
  - Validate against stylized facts across scenarios.
- **Scenario & stress testing**
  - Add scenario templates (low-liquidity, high-vol, multi-event).
  - Add parameter sweeps and sensitivity analysis.
