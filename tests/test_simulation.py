import numpy as np

from market_simulation.config import SimulationConfig
from market_simulation.simulation import run_simulation


def test_simulation_reproducible():
    config = SimulationConfig(
        run_id=1,
        T=50,
        has_event=False,
        event_time=None,
        jump_size=0.0,
        jump_direction=0,
        volatility=0.02,
        n_noise_traders=3,
        n_market_makers=1,
        n_prop_traders=1,
        insider_specs=[],
        seed=1234,
    )

    result_a = run_simulation(config)
    result_b = run_simulation(config)

    assert np.allclose(result_a.mid_prices, result_b.mid_prices)
    assert np.allclose(result_a.fundamental_values, result_b.fundamental_values)

    trades_a = result_a.trades_frame()
    trades_b = result_b.trades_frame()
    assert trades_a.equals(trades_b)
