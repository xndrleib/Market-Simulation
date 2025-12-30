# Usage

## Quick start

```python
from market_simulation import (
    SimulationConfig,
    configure_logging,
    generate_dataset,
    run_simulation,
)

logger = configure_logging(run_id=0)

config = SimulationConfig(run_id=0, seed=123)
result = run_simulation(config, logger=logger)
trades_df = result.trades_frame()

print(trades_df.head())
```

## Dataset generation

```python
from market_simulation import configure_logging, generate_dataset

logger = configure_logging()
frames = generate_dataset(n_runs=50, window_size=50, base_seed=123, logger=logger)

agent_df = frames["agent_level"]
window_df = frames["window_level"]
```

## Notes

- To keep results deterministic, pass explicit seeds to `SimulationConfig` or use `base_seed` when generating datasets.
- Logging writes to both console and `logs/market_simulation*.log`.
