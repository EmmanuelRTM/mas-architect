"""Load a multi-agent system spec from JSON (always) or YAML (if PyYAML is installed)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SPEC_SUFFIXES = (".mas.json", ".mas.yaml", ".mas.yml")


class SpecLoadError(ValueError):
    """The file is missing, unreadable or not a JSON/YAML object."""


def is_spec_path(path: str | Path) -> bool:
    return str(path).lower().endswith(SPEC_SUFFIXES)


def loads_spec(text: str, suffix: str = ".json") -> dict[str, Any]:
    if suffix.lower() in (".yaml", ".yml"):
        data = _loads_yaml(text)
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SpecLoadError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise SpecLoadError("the spec must be a JSON/YAML object at the top level")
    return data


def load_spec(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecLoadError(f"cannot read {path}: {exc.strerror or exc}") from exc
    return loads_spec(text, suffix=path.suffix)


def _loads_yaml(text: str) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        raise SpecLoadError("YAML specs need PyYAML; install it or use .mas.json") from exc
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise SpecLoadError(f"invalid YAML: {exc}") from exc
