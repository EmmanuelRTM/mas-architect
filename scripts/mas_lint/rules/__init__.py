"""Importing this package registers every rule module."""

from . import (  # noqa: F401  (imported for their @register side effect)
    baseline,
    coordination,
    diversity,
    fit,
    hygiene,
    merge_verify,
    models,
    monitoring,
    platform,
    schema,
    selection,
    skills,
    state,
)
from .base import Rule, registered

__all__ = ["Rule", "registered"]
