"""DIS v2 project route + stage-exit core (controlled paths only).

This module cannot intercept ChatGPT/Figma/Codex native calls and cannot
authenticate a human. Actual approval requires a trusted issuer AND a verified
remote GitHub write via a separate transport. No agent-authored flags can grant
themselves approval.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

from tools.enforcement.pcs_controller import verify_approval

SCHEMA = "DIS-PROJECT-STATE/v2"
STOP = "STOP_DIS_V2"
STRATEGIES = ("express", "guided", "strategic", "reference_led")
DESIGNS = ("hero_only", "homepage")
RESEARCH = ("screen", "homepage", "whole_site", "full_product")

ORDER = (
    "bootstrap", "intake", "project_configuration", "discovery",
    "market_competitive", "product_content_strategy",
    "information_architecture", "semantic_architecture", "prototype",
    "reference_intelligence", "art_direction", "seed_ui_kit",
    "creative_synthesis", "hero_concept", "hero_review",
    "homepage_sections", "full_page_review", "final_approval",
    "artifact_delivery",
)
CORE = (
    "bootstrap", "intake", "project_configuration", "discovery",
    "semantic_architecture", "reference_intelligence", "art_direction",
    "seed_ui_kit", "creative_synthesis", "hero_concept", "hero_review",
    "final_approval", "artifact_delivery",
)
PRESETS = {
    "express": CORE,
    "guided": CORE + ("market_competitive", "prototype"),
    "strategic": CORE + (
        "market_competitive", "product_content_strategy",
        "information_architecture", "prototype",
    ),
    "reference_led": CORE,
}
STATUS = {
    "IN_PROGRESS", "NEEDS_WORK", "BLOCKED",
    "READY_FOR_AUTHOR_REVIEW", "PENDING_SAVE", "APPROVED",
}
REVIEW_CHOICES = ("deepen", "revise", "approve")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")


def _digest(raw):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def _fail(*messages):
    return {"allowed": False, "code": STOP, "errors": list(messages)}


def describe_routes():
    """Present options; never make the operator's choice on their behalf."""
    return [
        {"id": "express", "label": "Express Concept",
         "purpose": "Scoped hypothesis-based concept with explicit uncertainty",
         "omits": ["extended IA", "additional UX prototype", "full market study"]},
        {"id": "guided", "label": "Guided Design",
         "purpose": "Research, UX structure and visual-direction checkpoints",
         "omits": ["full-product strategy unless separately selected"]},
        {"id": "strategic", "label": "Strategic Design",
         "purpose": "Broader product research, IA and content strategy",
         "omits": ["building every future product page by default"]},
        {"id": "reference_led", "label": "Reference-Led",
         "purpose": "Adapt reference principles to validated project needs",
         "omits": ["automatic copying of reference pixels or brand"]},
    ]


def compile_route(config):
    """Validate user-supplied three scopes and build one ordered stage plan.

    A positive result means a valid route *proposal*, not an author approval.
    """
    if not isinstance(config, dict):
        return _fail("route configuration must be an object")
    errors = []
    strategy = config.get("strategy")
    scopes = config.get("scopes")
    if strategy not in STRATEGIES:
        errors.append("strategy must be one of four offered choices")
    if not isinstance(scopes, dict):
        errors.append("three independent scopes required")
        scopes = {}
    research = scopes.get("research")
    design = scopes.get("design")
    delivery = scopes.get("delivery")
    if research not in RESEARCH:
        errors.append("invalid/missing research scope")
    if design not in DESIGNS:
        errors.append("invalid/missing design scope")
    if not isinstance(delivery, list) or not delivery or any(
        not isinstance(x, str) or not x.strip() for x in delivery
    ):
        errors.append("delivery scope must list desired artifacts")
    elif len(delivery) != len(set(delivery)):
        errors.append("duplicate delivery artifact")
    if errors:
        return _fail(*errors)

    selected = set(PRESETS[strategy])
    if design == "homepage":
        selected.update(("homepage_sections", "full_page_review"))
    extras = config.get("extra_modules", [])
    if not isinstance(extras, list) or any(x not in ORDER for x in extras):
        return _fail("invalid extra_modules")
    selected.update(extras)
    omit = config.get("omit_modules", [])
    if not isinstance(omit, list) or any(x not in ORDER for x in omit):
        return _fail("invalid omit_modules")
    if any(x in CORE for x in omit):
        return _fail("cannot omit core stage without an approved alternative route")
    if design == "homepage" and any(
        x in ("homepage_sections", "full_page_review") for x in omit
    ):
        return _fail("full homepage requires section production and page review")
    # Omissions beyond preset must be intentionally justified; user-reviewed
    # route confirmation happens separately in a trusted approval channel.
    exceptions = config.get("scope_adaptations", [])
    if not isinstance(exceptions, list):
        return _fail("scope_adaptations must be a list")
    for mod in omit:
        justified = any(
            isinstance(e, dict) and e.get("stage") == mod and
            isinstance(e.get("reason"), str) and e.get("reason").strip() and
            isinstance(e.get("decision_ref"), str) and e.get("decision_ref").strip()
            for e in exceptions
        )
        if not justified:
            return _fail("missing explicit rationale for omitted module: " + mod)
        selected.discard(mod)
    ordered = [name for name in ORDER if name in selected]
    if ordered.index("hero_concept") >= ordered.index("hero_review"):
        return _fail("HERO review must follow HERO concept")
    if design == "homepage" and not (
        ordered.index("hero_review") < ordered.index("homepage_sections") <
        ordered.index("full_page_review") < ordered.index("final_approval")
    ):
        return _fail("homepage stage dependencies invalid")
    return {"allowed": True, "code": "ROUTE_CANDIDATE_NOT_APPROVED",
            "strategy": strategy,
            "scopes": copy.deepcopy(scopes),
            "stage_plan": ordered,
            "selected_by_author": False,
            "warning": "Route options/configuration are not author approvals."}


def _safe_file(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("invalid evidence path")
    base = Path(root).resolve()
    file = (base / relative).resolve()
    if not file.is_relative_to(base) or not file.is_file():
        raise ValueError("unsafe or missing evidence path")
    return file


def validate_state(state):
    """Validate the remote state *structure*, not authenticity or approvals."""
    if not isinstance(state, dict) or state.get("schema") != SCHEMA:
        return _fail("project state schema mismatch")
    errors = []
    repo = state.get("project_repo")
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        errors.append("invalid or missing project repo")
    sha = state.get("methodology_revision")
    if not isinstance(sha, str) or not COMMIT_RE.fullmatch(sha):
        errors.append("methodology commit SHA required")
    route = state.get("route")
    active = state.get("active_stage")
    if route is None:
        # A new private project must be creatable BEFORE the operator chooses
        # the strategy. Never silently assign "guided" as a default.
        if active not in ("bootstrap", "intake", "project_configuration"):
            errors.append("route must be selected before research/production")
    else:
        compiled = compile_route(route)
        if not compiled["allowed"]:
            errors.extend(compiled["errors"])
        elif route.get("stage_plan") != compiled["stage_plan"]:
            errors.append("stage_plan differs from configured route")
        if compiled["allowed"] and active not in compiled["stage_plan"]:
            errors.append("active stage absent from selected route")
    if state.get("stage_status") not in STATUS:
        errors.append("invalid stage status")
    if not isinstance(state.get("stage_version"), str) or not state["stage_version"]:
        errors.append("stage version missing")
    if not isinstance(state.get("decisions"), list):
        errors.append("decision register missing")
    if not isinstance(state.get("acceptance_criteria"), list):
        errors.append("pre-agreed stage acceptance criteria missing")
    if not isinstance(state.get("history"), list):
        errors.append("stage history missing")
    if "review_gates" in state and not isinstance(state["review_gates"], dict):
        errors.append("review gate evidence must be a dictionary")
    return _fail(*errors) if errors else {"allowed": True, "code": "STRUCTURE_VALID_ONLY"}


def _start_payload(state):
    """SSA binds agreed *definitions*, not evolving work/results/evidence.

    Criteria descriptions/classes are frozen. Status/evidence is mutable
    within the same stage. New research findings, execution ledgers and
    proposed decisions do not revoke the stage-start authorization.
    To alter scope, criterion definitions or accepted upstream baseline,
    create a revised SSA and stage version instead.
    """
    definitions = []
    for item in state["acceptance_criteria"]:
        if not isinstance(item, dict):
            definitions.append(item)
        else:
            definitions.append({
                k: v for k, v in item.items()
                if k not in ("status", "evidence", "observed_at", "notes")
            })
    return {
        "project_repo": state["project_repo"],
        "methodology_revision": state["methodology_revision"],
        "active_stage": state["active_stage"],
        "stage_version": state["stage_version"],
        "route": state.get("route"),
        "criteria_definitions": definitions,
        "approved_input_decisions": state.get("approved_input_decisions", []),
        "approved_start_sources": state.get("approved_start_sources", []),
    }


def _exit_payload(state):
    """Snapshot bound to the exact author-visible result and criteria."""
    return {
        "project_repo": state["project_repo"],
        "methodology_revision": state["methodology_revision"],
        "route": state["route"],
        "active_stage": state["active_stage"],
        "stage_version": state["stage_version"],
        "acceptance_criteria": state["acceptance_criteria"],
        "decisions": state["decisions"],
        "result_artifact": state.get("result_artifact"),
        "review_gates": state.get("review_gates"),
        "hypotheses": state.get("hypotheses", []),
    }


def stage_exit(state, root):
    """A structural exit check; artistic/content truth still needs review."""
    v = validate_state(state)
    if not v["allowed"]:
        return v
    if state["stage_status"] == "APPROVED":
        return {"allowed": True, "code": "ALREADY_APPROVED_PREPARE_NEXT_PACKET",
                "next_stage_can_start": False}
    if state["stage_status"] == "PENDING_SAVE":
        return _fail("approval pending remote GitHub commit/readback")

    criteria = state["acceptance_criteria"]
    if not criteria:
        return _fail("no acceptance criteria agreed before stage execution")
    results = []
    blocking = []
    seen = set()
    for criterion in criteria:
        if not isinstance(criterion, dict) or not criterion.get("id"):
            return _fail("invalid criterion record")
        ident = criterion["id"]
        if ident in seen:
            return _fail("duplicate criterion id")
        seen.add(ident)
        kind = criterion.get("class")
        if kind not in ("REQUIRED", "JUDGEMENT", "OPTIONAL", "DEPENDENT"):
            return _fail("invalid criterion class")
        status = criterion.get("status", "NOT_CHECKED")
        if status not in ("PASS", "FAIL", "NOT_CHECKED", "OPEN"):
            return _fail("invalid criterion status")
        evidence = criterion.get("evidence")
        checked = False
        issue = ""
        if status == "PASS":
            try:
                path = evidence.get("path") if isinstance(evidence, dict) else None
                digest = evidence.get("sha256") if isinstance(evidence, dict) else None
                if not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
                    raise ValueError("evidence digest missing/invalid")
                checked = _digest(_safe_file(root, path).read_bytes()) == digest
                if not checked:
                    issue = "evidence content SHA256 mismatch"
            except (OSError, ValueError, TypeError) as exc:
                issue = str(exc)
        effective = "PASS" if checked else (
            "FAIL" if status == "FAIL" else "NOT_CHECKED"
        )
        if kind == "REQUIRED" and effective != "PASS":
            blocking.append(ident)
        if kind == "DEPENDENT" and criterion.get("blocks_next_action") and effective != "PASS":
            blocking.append(ident)
        results.append({"id": ident, "class": kind, "status": effective,
                        "evidence_verified": checked, "issue": issue})
    summary = {
        "stage": state["active_stage"], "version": state["stage_version"],
        "scope": state["route"]["scopes"] if state.get("route") else {"configuration": "pending"},
        "decisions": copy.deepcopy(state["decisions"]),
        "checks": results,
        "open_hypotheses": copy.deepcopy(state.get("hypotheses", [])),
        "recommended_action": "revise" if blocking else "review_author_choices",
        "operator_choices": ("deepen", "revise") if blocking else REVIEW_CHOICES,
        "snapshot_sha256": _digest(_canonical(_exit_payload(state))),
    }
    return {
        "allowed": not blocking,
        "code": "READY_FOR_AUTHOR_REVIEW" if not blocking else "NEEDS_WORK",
        "blocking": blocking, "summary": summary,
        "warning": "File-integrity checks are NOT independent editorial/design quality checks.",
    }


def request_next_stage(state, root):
    """Official intent 'Переходим к следующему этапу' is NOT approval."""
    v = validate_state(state)
    if not v["allowed"]:
        return v
    if state["stage_status"] == "APPROVED":
        # Caller must establish that this state was read from the verified
        # GitHub project ref. A local agent-authored state is insufficient.
        return {"allowed": True, "code": "PREPARE_NEXT_STAGE_PACKET_ONLY",
                "start_requires_separate_SSA": True}
    return stage_exit(state, root)


def verify_author_stage_approval(state, receipt, signing_key, root):
    """Privileged-service operation; the agent must NOT possess signing_key."""
    check = stage_exit(state, root)
    if not check.get("allowed") or check["code"] != "READY_FOR_AUTHOR_REVIEW":
        return _fail("stage not ready for author approval")
    if not signing_key:
        return _fail("independent approval issuer not connected")
    snapshot = check["summary"]["snapshot_sha256"]
    verified = verify_approval(
        snapshot, receipt, "stage_result", state["active_stage"],
        (state["route"]["scopes"]["design"] if state.get("route") else "bootstrap"), signing_key,
    )
    if not verified["allowed"]:
        return _fail("untrusted/mismatched author approval: " + verified["code"])
    # Draft for remote save; do not claim APPROVED until GitHub confirms bytes.
    new_state = copy.deepcopy(state)
    new_state["stage_status"] = "APPROVED"
    new_state.setdefault("history", []).append({
        "stage": state["active_stage"],
        "version": state["stage_version"],
        "result_snapshot_sha256": snapshot,
        "approval_receipt": copy.deepcopy(receipt),
        "approval_actor": verified.get("actor"),
    })
    return {"allowed": True, "code": "READY_FOR_GITHUB_WRITE_NOT_APPROVED",
            "candidate_state": new_state, "snapshot_sha256": snapshot,
            "warning": "Approved ONLY after expected GitHub commit and readback."}
