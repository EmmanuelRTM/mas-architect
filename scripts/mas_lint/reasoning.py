"""Detect instructions that ask a model to write its reasoning into the reply.

Fable 5.1, Opus 5.5 and Sonnet 5.5 may decline such prompts with the
`reasoning_extraction` refusal category; Haiku 5.5 may leak reasoning-like
text instead. Ask for a short explanation or a summary of actions, or read
summarized thinking blocks. English and Spanish phrasings are covered.
"""

from __future__ import annotations

import re

_PATTERNS = (
    re.compile(
        r"\b(show|write out|spell out|output|print|include|reproduce|transcribe|echo|explain)\b[^.\n]{0,40}"
        r"\b(your|the|its)\s+(full\s+)?(reasoning|thinking|thought process|chain[- ]of[- ]thought)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bstep[- ]by[- ]step\b[^.\n]{0,60}\b(in|into)\s+(the|your)\s+(final\s+)?(answer|response|reply|output)\b", re.IGNORECASE),
    re.compile(
        r"\b(muestra|muestre|explica|explique|escribe|escriba|incluye|incluya|detalla|detalle)\b[^.\n]{0,40}"
        r"\b(tu|su|el)\s+(razonamiento|pensamiento|proceso de pensamiento)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bpaso a paso\b[^.\n]{0,60}\b(en|dentro de)\s+(la|tu|su)\s+(respuesta|salida)\b", re.IGNORECASE),
)


def asks_for_visible_reasoning(text: str) -> bool:
    return any(p.search(text) for p in _PATTERNS)
