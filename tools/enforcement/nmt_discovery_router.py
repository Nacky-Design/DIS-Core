"""NMT external-skill discovery routing, without copying licensed skill files.

Availability and license rights are distinct. Finding an SKILL.md does NOT
prove the copyright holder authorized commercial use, nor that the agent has
actually run it. No automatic network installation.
"""
from pathlib import Path

NMT_SOURCE = "https://github.com/zamesin/Next-Move-Theory-Canon-and-Skills"
NMT_LICENSE = "CC-BY-NC-SA-4.0"
NMT_SKILLS = (
    "nmt-chat", "nmt-market-research", "nmt-diagnose",
    "nmt-analyze-interviews", "nmt-craft-value-proposition",
    "nmt-product-requirements", "nmt-craft-go-to-market",
)


def choose_nmt_skill(*, is_live=False, interviews=False, market_choice=False,
                     value_proposition=False, requirements=False,
                     go_to_market=False):
    """Recommend one explicit intent; do not start any skill implicitly."""
    if interviews:
        name = "nmt-analyze-interviews"
    elif is_live:
        name = "nmt-diagnose"
    elif market_choice:
        name = "nmt-market-research"
    elif value_proposition:
        name = "nmt-craft-value-proposition"
    elif requirements:
        name = "nmt-product-requirements"
    elif go_to_market:
        name = "nmt-craft-go-to-market"
    else:
        name = "nmt-chat"
    return {"selected": name, "other_available": list(NMT_SKILLS),
            "auto_execute": False}


def check_nmt_connection(project_root, *, skill, commercial_use=True,
                         explicit_rights=False):
    if skill not in NMT_SKILLS:
        return {"allowed": False, "code": "STOP_UNKNOWN_NMT_SKILL"}
    root = Path(project_root).resolve()
    candidate = (root / ".agents" / "skills" / skill / "SKILL.md").resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        return {"allowed": False, "code": "NMT_NOT_CONNECTED",
                "source": NMT_SOURCE, "selected_skill": skill,
                "reason": "Skill not installed in this project environment"}
    if commercial_use and not explicit_rights:
        return {"allowed": False, "code": "NMT_RIGHTS_REVIEW_REQUIRED",
                "source": NMT_SOURCE, "license": NMT_LICENSE,
                "reason": "External noncommercial license; check rights before commercial use"}
    return {"allowed": True, "code": "NMT_SKILL_FILE_PRESENT_RIGHTS_DECLARED",
            "selected_skill": skill,
            "warning": "File check does not prove skill execution or methodology quality."}
