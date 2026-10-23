"""Team-size arithmetic from the research synthesis.

With pairwise error correlation rho, the effective team size is
N_eff = N / (1 + (N - 1) * rho), which tends to 1 / rho as N grows
(arXiv 2609.31563). At rho = 0.9, thirty agents behave like about 1.1.
"""

from __future__ import annotations

import math
from typing import Any

from .accessors import (
    agents,
    generator_instances,
    generators,
    get,
    is_number,
    total_instances,
)


def effective_team_size(n: int, rho: float) -> float:
    if n < 1:
        raise ValueError("team size must be at least 1")
    if not 0.0 <= rho <= 1.0:
        raise ValueError("error correlation must be between 0 and 1")
    return n / (1 + (n - 1) * rho)


def saturation_size(rho: float) -> float:
    """The asymptote of N_eff: adding agents past a few multiples of this buys little."""
    return math.inf if rho == 0 else 1 / rho


def compute_metrics(spec: dict) -> dict[str, Any]:
    gens = generators(spec)
    candidates = get(spec, "selection.candidates")
    rho = get(spec, "budget.expected_error_correlation")
    metrics: dict[str, Any] = {
        "agents_defined": len(agents(spec)),
        "total_instances": total_instances(spec),
        "generator_instances": generator_instances(spec),
        "model_families": len({a.get("model_family") for a in gens if a.get("model_family")}),
        "distinct_models": len({a.get("model") for a in gens if a.get("model")}),
        "candidates": candidates if isinstance(candidates, int) else None,
        "error_correlation": rho if is_number(rho) else None,
        "effective_team_size": None,
        "saturation_size": None,
    }
    replicas = metrics["candidates"] or metrics["generator_instances"]
    if is_number(rho) and 0 <= rho <= 1 and replicas:
        metrics["effective_team_size"] = round(effective_team_size(replicas, rho), 3)
        sat = saturation_size(rho)
        metrics["saturation_size"] = None if math.isinf(sat) else round(sat, 3)
    return metrics
