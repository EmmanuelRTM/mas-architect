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
    title_es: str


PRACTICES: tuple[Practice, ...] = (
    Practice("P1", "Measure the strong single-agent baseline first", "Medir primero la línea base de un solo agente fuerte"),
    Practice("P2", "Generate independently across diverse model families", "Generar de forma independiente con familias de modelos diversas"),
    Practice("P3", "Spend on selection, not on more voters", "Invertir en selección, no en más votantes"),
    Practice("P4", "Keep state in the harness; agents are disposable", "Estado en el harness; agentes desechables"),
    Practice("P5", "Cap every read (top-K, prune tools, drop stale output)", "Acotar cada lectura (top-K, podar herramientas)"),
    Practice("P6", "Non-blocking communication and explicit ownership", "Comunicación no bloqueante y dueños explícitos"),
    Practice("P7", "Hand raw evidence, not summaries, to the merger", "Pasar evidencia cruda, no resúmenes, al que fusiona"),
    Practice("P8", "Separate the judge from the generator", "Separar al juez del generador"),
    Practice("P9", "Monitor beliefs and repeated runs, not only transcripts", "Monitorear creencias y corridas repetidas"),
    Practice("P10", "Train with team-level credit and decorrelated agents", "Entrenar con crédito de equipo y agentes decorrelacionados"),
    Practice("MOD", "Assign model and effort per role deliberately", "Asignar modelo y esfuerzo por rol a propósito"),
    Practice("OPS", "Respect platform limits, schema and hygiene", "Respetar límites de plataforma, esquema e higiene"),
)

PRACTICE_IDS = tuple(p.id for p in PRACTICES)
