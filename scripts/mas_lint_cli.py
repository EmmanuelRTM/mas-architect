#!/usr/bin/env python3
"""Command line for the mas-architect linter.

    python3 mas_lint_cli.py lint SPEC [--format text|json] [--no-info]
    python3 mas_lint_cli.py recommend SPEC
    python3 mas_lint_cli.py rules [--markdown]
    python3 mas_lint_cli.py neff N RHO

Exit codes: 0 ok, 1 lint errors, 2 bad input.
"""

from __future__ import annotations

import argparse
import json
import sys

from mas_lint import SpecLoadError, lint, load_spec
from mas_lint.definitions import DEFINITION_RULES
from mas_lint.formatting import format_text
from mas_lint.metrics import effective_team_size, saturation_size
from mas_lint.rules import registered


def cmd_lint(args) -> int:
    report = lint(load_spec(args.spec))
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(format_text(report, include_info=not args.no_info))
    return 1 if report.has_errors else 0


def cmd_recommend(args) -> int:
    report = lint(load_spec(args.spec))
    print(f"{'agent':24} {'role':12} {'n':>3}  {'current':28} recommended")
    for row in report.agents:
        current = f"{row['model']}@{row['effort'] or '-'}" + ("*" if row["effort_is_default"] else "")
        rec = f"{row['recommended']['model']}@{row['recommended']['effort']}"
        print(f"{str(row['id']):24} {str(row['role']):12} {row['count']:>3}  {current:28} {rec}")
    print("\n* effort not set: model default shown. Sweep efforts on your own evals before fixing them.")
    return 0


def cmd_rules(args) -> int:
    if args.markdown:
        print(rules_markdown())
        return 0
    for rule in registered():
        print(f"{rule.id}  {rule.practice:4} {rule.title}")
    return 0


def rules_markdown() -> str:
    """The two tables of docs/RULES.md, so the doc can be regenerated from the code."""
    cell = lambda text: " ".join(str(text).split()).replace("|", "\\|")  # noqa: E731
    lines = ["## Spec rules (`*.mas.json`)", "", "| Rule | Practice | What it checks | Evidence |", "|---|---|---|---|"]
    lines += [f"| {r.id} | {r.practice} | {cell(r.title)} | {cell(r.evidence)} |" for r in registered()]
    lines += ["", "## Definition rules (`agents/*.md`, `skills/*/SKILL.md`)", "", "| Rule | Severity | What it checks |", "|---|---|---|"]
    lines += [f"| {rid} | {severity} | {what} |" for rid, severity, what in DEFINITION_RULES]
    return "\n".join(lines)


def cmd_neff(args) -> int:
    n_eff = effective_team_size(args.n, args.rho)
    print(f"N_eff = {n_eff:.3f} (ceiling 1/rho = {saturation_size(args.rho):.3f})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mas-lint", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_lint = sub.add_parser("lint", help="lint a .mas.json spec")
    p_lint.add_argument("spec")
    p_lint.add_argument("--format", choices=("text", "json"), default="text")
    p_lint.add_argument("--no-info", action="store_true")
    p_lint.set_defaults(func=cmd_lint)
    p_rec = sub.add_parser("recommend", help="model and effort per agent vs the role table")
    p_rec.add_argument("spec")
    p_rec.set_defaults(func=cmd_recommend)
    p_rules = sub.add_parser("rules", help="list every rule")
    p_rules.add_argument("--markdown", action="store_true", help="print the docs/RULES.md tables")
    p_rules.set_defaults(func=cmd_rules)
    p_neff = sub.add_parser("neff", help="effective team size for N agents at error correlation RHO")
    p_neff.add_argument("n", type=int)
    p_neff.add_argument("rho", type=float)
    p_neff.set_defaults(func=cmd_neff)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (SpecLoadError, ValueError) as exc:
        print(f"mas-lint: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
