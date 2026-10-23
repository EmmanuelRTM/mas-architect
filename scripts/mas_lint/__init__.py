"""mas_lint: deterministic checks for multi-agent system designs.

Pure standard library. Public entry points:
    lint(spec) -> Report
    load_spec(path) -> dict
"""

from .engine import lint
from .loader import SpecLoadError, load_spec
from .model import Finding, Report, Severity

__all__ = ["Finding", "Report", "Severity", "SpecLoadError", "lint", "load_spec"]
__version__ = "0.1.0"
