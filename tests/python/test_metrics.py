import math

import pytest

from mas_lint.metrics import compute_metrics, effective_team_size, saturation_size


def test_effective_team_size_matches_paper_formula():
    # N_eff = N / (1 + (N - 1) * rho); 30 agents at rho 0.9 leave ~1.1.
    assert effective_team_size(30, 0.9) == pytest.approx(1.107, abs=1e-3)


def test_uncorrelated_team_keeps_full_size():
    assert effective_team_size(8, 0.0) == 8


def test_single_agent_is_one():
    assert effective_team_size(1, 0.7) == 1


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        effective_team_size(0, 0.5)
    with pytest.raises(ValueError):
        effective_team_size(3, 1.5)


def test_saturation_size_is_inverse_correlation():
    assert saturation_size(0.5) == 2
    assert math.isinf(saturation_size(0.0))


def test_compute_metrics_summarises_spec(base_spec):
    metrics = compute_metrics(base_spec)
    assert metrics["generator_instances"] == 8
    assert metrics["model_families"] == 3
    assert metrics["candidates"] == 8
    assert metrics["effective_team_size"] == pytest.approx(8 / (1 + 7 * 0.3), abs=1e-3)
