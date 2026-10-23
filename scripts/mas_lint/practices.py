"""The ten converging practices from the research synthesis, plus MOD and OPS.

Each lint rule belongs to exactly one practice; a practice's status in a
report is the worst severity among its rules' findings.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Practice:
    id: str
    title: str


PRACTICES: tuple[Practice, ...] = (
    Practice("P1", "Measure the strong single-agent baseline first"),
    Practice("P2", "Generate independently across diverse model families"),
    Practice("P3", "Spend on selection, not on more voters"),
    Practice("P4", "Keep state in the harness; agents are disposable"),
    Practice("P5", "Cap every read (top-K, prune tools, drop stale output)"),
    Practice("P6", "Non-blocking communication and explicit ownership"),
    Practice("P7", "Hand raw evidence, not summaries, to the merger"),
    Practice("P8", "Separate the judge from the generator"),
    Practice("P9", "Monitor beliefs and repeated runs, not only transcripts"),
    Practice("P10", "Train with team-level credit and decorrelated agents"),
    Practice("MOD", "Assign model and effort per role deliberately"),
    Practice("OPS", "Respect platform limits, schema and hygiene"),
)

PRACTICE_IDS = tuple(p.id for p in PRACTICES)
