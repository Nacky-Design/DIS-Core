"""DIS stage routing registry — explicit, testable v2 mapping.

No model-derived stage-to-prompt guesswork. Registry labels the actual
documentation or skill entry; an absent required source fails the preflight.
"""
from pathlib import Path

STAGE_REGISTRY = {
    "bootstrap": ("prompts/dis-project-bootstrap-v2.md", None),
    "intake": ("prompts/dis-project-bootstrap-v2.md", None),
    "project_configuration": ("prompts/dis-project-bootstrap-v2.md", None),
    "discovery": ("prompts/pcs-discovery-v1.1.md", None),
    "market_competitive": ("prompts/pcs-competitive-research-v1.1.md", None),
    "product_content_strategy": ("prompts/pcs-product-content-strategy-v1.md", None),
    "information_architecture": ("prompts/pcs-information-architecture-v1.md", None),
    "semantic_architecture": ("prompts/pcs-semantic-architecture-v1.1.md", None),
    "prototype": ("prompts/pcs-prototype-v1.1.md", None),
    "reference_intelligence": (
        "prompts/pcs-reference-intelligence-v1.1.md",
        ".agents/skills/dis-reference-intelligence/SKILL.md",
    ),
    "art_direction": ("prompts/pcs-art-direction-v1.1.md", None),
    "seed_ui_kit": ("prompts/pcs-ui-kit-v1.1.md", None),
    "creative_synthesis": (
        "prompts/pcs-frankenstein-v1.1.md",
        ".agents/skills/dis-visual-synthesis/SKILL.md",
    ),
    "hero_concept": ("prompts/pcs-fa01-v1.2.md", None),
    "hero_review": ("prompts/pcs-visual-concept-v1.1.md", None),
    "homepage_sections": ("prompts/pcs-fa01-v1.2.md", None),
    "full_page_review": ("prompts/pcs-fa02-v1.1.md", None),
    "final_approval": ("prompts/pcs-stage-result-v1.1.md", None),
    "artifact_delivery": ("prompts/pcs-artifact-delivery-v1.md", None),
}

# NOTE: shared prompts are adapters pending dedicated author-reviewed
# prompt contracts; the registry is a routing preflight, not evidence of
# content/UX/SEO phase completeness.
SHARED_PROMPT_REVIEW = {
    "final_approval",
}


def validate_stage_registry(dis_root, order):
    root = Path(dis_root).resolve()
    errors = []
    stages = set(order)
    extra = set(STAGE_REGISTRY) - stages
    missing = stages - set(STAGE_REGISTRY)
    if extra:
        errors.append("unknown registered stages: " + ", ".join(sorted(extra)))
    if missing:
        errors.append("unmapped stages: " + ", ".join(sorted(missing)))
    for stage, (prompt, skill) in STAGE_REGISTRY.items():
        for kind, name in (("prompt", prompt), ("skill", skill)):
            if name is None:
                continue
            candidate = (root / name).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                errors.append(f"{stage}: missing {kind} {name}")
    ref_prompt, ref_skill = STAGE_REGISTRY["reference_intelligence"]
    if "competitive" in ref_prompt:
        errors.append("Reference Intelligence may not run competitor prompt")
    if not ref_skill or "reference-intelligence" not in ref_skill:
        errors.append("Reference Intelligence requires its own skill")
    return {
        "allowed": not errors,
        "code": "STAGE_ROUTING_VALIDATED" if not errors else "STOP_STAGE_ROUTING",
        "errors": errors,
        "review_required": sorted(SHARED_PROMPT_REVIEW),
    }
