import pytest

from simulation.config import SimulationConfig

def test_default_config_values():
    config = SimulationConfig()
    
    assert config.motorbike_usage_rate == 0.8
    assert config.register_rate == 0.95
    assert config.sparse_rate == 0.15
    assert config.days_weights_distribution == (2, 5, 25, 32, 28, 8)

@pytest.mark.parametrize("field", ["motorbike_usage_rate", "register_rate", "sparse_rate"])
@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_rate_out_of_range_raises(field, value):
    with pytest.raises(ValueError):
        SimulationConfig(**{field: value})


def test_weights_length_must_match_days():
    with pytest.raises(ValueError):
        SimulationConfig(days_weights_distribution=(1, 2, 3))


def test_negative_weight_raises():
    with pytest.raises(ValueError):
        SimulationConfig(days_weights_distribution=(10, 10, 10, 10, 10, -1))


def test_all_zero_weights_raise():
    with pytest.raises(ValueError):
        SimulationConfig(days_weights_distribution=(0, 0, 0, 0, 0, 0))


def test_sparse_rate_needs_three_sessions():
    with pytest.raises(ValueError):
        SimulationConfig(sessions_per_day=2)
    SimulationConfig(sessions_per_day=2, sparse_rate=0.0)


def test_sessions_per_day_must_be_positive():
    with pytest.raises(ValueError):
        SimulationConfig(sessions_per_day=0, sparse_rate=0.0)