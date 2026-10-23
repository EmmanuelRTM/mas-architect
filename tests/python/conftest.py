"""Shared fixtures for the mas_lint test suite."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "templates" / "examples"
FIXTURES = ROOT / "tests" / "fixtures"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _deep_merge(base: dict, overrides: dict) -> dict:
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


@pytest.fixture
def example_paths() -> list[Path]:
    return sorted(EXAMPLES.glob("*.mas.json"))


@pytest.fixture
def antipattern_path() -> Path:
    return FIXTURES / "antipatterns.mas.json"


@pytest.fixture
def base_spec() -> dict:
    """A clean spec (the QA example) that lints with no errors or warnings."""
    return json.loads((EXAMPLES / "qa-selector.mas.json").read_text())


@pytest.fixture
def make_spec(base_spec):
    """Build a spec from the clean base with nested overrides applied."""

    def build(**overrides) -> dict:
        return _deep_merge(base_spec, overrides)

    return build


@pytest.fixture
def rule_ids():
    """Run the linter and return the ids of findings at or above a severity."""
    from mas_lint import lint

    def run(spec: dict, severities=("error", "warning")) -> set[str]:
        report = lint(spec)
        return {f.rule_id for f in report.findings if f.severity.value in severities}

    return run
