"""Skills per agent: declare them, keep them few, and keep judges off the generators' playbook."""

from __future__ import annotations

from ..accessors import GENERATOR_ROLES, JUDGE_ROLES, agent_path, agent_skills, agents, skill_catalog
from ..skill_refs import MAX_PRELOADED_SKILLS, bare_name
from .base import Rule, register


@register
class SkillsDeclaredRule(Rule):
    id = "MAS029"
    title = "Every agent states which skills it preloads"
    practice = "P5"
    evidence = "Subagents do not inherit the parent's skills; an undeclared playbook is either missing or loaded ad hoc."

    def check(self, spec):
        for agent in agents(spec):
            if agent_skills(agent) is None:
                yield self.info(
                    f"Agent `{agent.get('id', '?')}` has no `skills` list. Name the skills this role runs every time, or `[]` for none.",
                    agent_path(agent, "skills"),
                )


@register
class SkillsInCatalogRule(Rule):
    id = "MAS030"
    title = "Agent skills exist in the spec's skill catalog"
    practice = "OPS"
    evidence = "Claude Code skips an unresolved skill with only a warning, so the agent silently runs without it."

    def check(self, spec):
        catalog = skill_catalog(spec)
        if catalog is None:
            return
        for agent in agents(spec):
            missing = [s for s in agent_skills(agent) or [] if bare_name(s) not in catalog and s not in catalog]
            if missing:
                yield self.warning(
                    f"Agent `{agent.get('id', '?')}` preloads {', '.join(missing)}, which the top-level `skills` catalog does not list.",
                    agent_path(agent, "skills"),
                )


@register
class PreloadBudgetRule(Rule):
    id = "MAS031"
    title = f"At most {MAX_PRELOADED_SKILLS} preloaded skills per agent"
    practice = "P5"
    evidence = "Each preloaded skill injects its whole SKILL.md at startup; context growth is a binding constraint."

    def check(self, spec):
        for agent in agents(spec):
            skills = agent_skills(agent) or []
            if len(skills) > MAX_PRELOADED_SKILLS:
                yield self.warning(
                    f"Agent `{agent.get('id', '?')}` preloads {len(skills)} skills. Keep at most {MAX_PRELOADED_SKILLS}; split the role or let the rest load on demand.",
                    agent_path(agent, "skills"),
                )


@register
class JudgeSkillIndependenceRule(Rule):
    id = "MAS032"
    title = "Judges do not preload the generators' playbook"
    practice = "P8"
    evidence = "A judge primed with the same heuristics as the generators shares their blind spots (correlated errors, self-preference)."

    def check(self, spec):
        generator_skills: set[str] = set()
        for agent in agents(spec):
            if agent.get("role") in GENERATOR_ROLES:
                generator_skills.update(bare_name(s) for s in agent_skills(agent) or [])
        for agent in agents(spec):
            if agent.get("role") not in JUDGE_ROLES:
                continue
            shared = sorted({bare_name(s) for s in agent_skills(agent) or []} & generator_skills)
            if shared:
                yield self.warning(
                    f"Judge `{agent.get('id', '?')}` preloads the generators' skills ({', '.join(shared)}). Give it a rubric or verification skill instead.",
                    agent_path(agent, "skills"),
                )
