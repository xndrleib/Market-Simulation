from market_simulation.config import sample_random_config


def test_sample_random_config_deterministic_without_rng():
    config_a = sample_random_config(run_id=7)
    config_b = sample_random_config(run_id=7)

    assert config_a == config_b
