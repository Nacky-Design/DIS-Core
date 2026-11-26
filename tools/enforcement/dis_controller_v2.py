"""DIS v2 controlled orchestration of PCS / DEC / RQC / STG / GitHub.

A thin composition layer. Its entrypoints explicitly verify the applicable
contracts in a fixed order. They do NOT intercept native ChatGPT/Figma/Codex,
act as an authenticated author, or issue signed approvals.

The trusted issuer's signing secret must be accessible to the privileged
controller process only. The creative agent must never own it.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from tools.enforcement.dec_controller import (
    audit_actual_artifact, validate_pre_execution,
)
from tools.enforcement.dis_project_v2 import (
    _canonical, _digest, _start_payload, compile_route,
    request_next_stage, stage_exit,
    verify_author_stage_approval,
)
from tools.enforcement.github_project_state import commit_state, load_project
from tools.enforcement.pcs_controller import verify_approval
from tools.enforcement.research_quality_gate import validate as validate_research
from tools.enforcement.stage_guard import check as check_stage_guard

DISCOVERY = {"discovery", "market_competitive"}
VISUAL = {
    "hero_concept", "hero_review", "homepage_sections", "full_page_review",
}
PRODUCTION_ACTIONS = {
    "image_generation", "visual_concept", "figma_write", "html_production",
}
REVIEW_GATE_STATUS = {
    "DEC_PRE_EXEC_PASS", "DEC_ARTIFACT_READY",
    "RQC_STRUCTURE_READY", "STG_ALLOW",
}

NONPRODUCTION_ACTIONS = {
    "research_review", "research_report", "reference_research",
    "stage_review", "prototype_work", "semantic_work",
    "propose_art_direction", "artifact_delivery",
}


def _allowed_for_stage(stage, action):
    if action in PRODUCTION_ACTIONS:
        return stage in VISUAL
    if stage in VISUAL:
        return False
    if action in ("research_review", "research_report"):
        return stage in DISCOVERY
    if action == "reference_research":
        return stage == "reference_intelligence"
    if action == "propose_art_direction":
        return stage == "art_direction"
    if action == "prototype_work":
        return stage == "prototype"
    if action == "semantic_work":
        return stage == "semantic_architecture"
    if action == "artifact_delivery":
        return stage == "artifact_delivery"
    return action == "stage_review" and stage not in VISUAL



def stop(reason, code="STOP_DIS_CONTROLLER"):
    return {"allowed": False, "code": code, "reason": reason}


def _read_pinned_json(root, record):
    if not isinstance(record, dict):
        raise ValueError("missing pinned record")
    relative = record.get("path")
    expected = record.get("sha256")
    if (not isinstance(relative, str) or not relative or
            not isinstance(expected, str) or len(expected) != 64):
        raise ValueError("missing source filename/hash")
    base = Path(root).resolve()
    path = (base / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(base):
        raise ValueError("unsafe evidence path")
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError("stale/mismatched " + relative)
    return json.loads(content)


def _project_scope(state):
    return (state["route"]["scopes"]["design"]
            if state.get("route") else "bootstrap")


def _start_snapshot(state):
    return _start_payload(state)

def check_start_authorization(state, receipt, signing_key):
    if not signing_key:
        return stop("trusted stage start approval issuer not connected")
    digest = _digest(_canonical(_start_snapshot(state)))
    verified = verify_approval(digest, receipt, "stage_start",
                               state["active_stage"], _project_scope(state),
                               signing_key)
    if not verified["allowed"]:
        return stop(verified["code"], "STOP_SSA_001")
    return {"allowed": True, "code": "SSA_VERIFIED",
            "start_snapshot_sha256": digest}


def _pcs_view(state, execution):
    """Use existing DEC schema, never fake missing approved source records."""
    return {
        "project": execution["project"],
        "stage_id": state["active_stage"],
        "scope": _project_scope(state),
        "sources": execution.get("sources", []),
        "decisions": state["decisions"],
        "prompt": execution["prompt"],
    }


def review_execution(state, root, *, action, start_receipt, signing_key):
    """Pre-production check: SSA => source pinned DEC => RQC => STG.

    No UI/tool production should occur on the controlled route before ALL
    applicable checks return allowed. No bypass of missing mandatory ledger.
    """
    if not isinstance(state, dict) or not isinstance(state.get("execution"), dict):
        return stop("missing stage execution inputs")
    if action not in (PRODUCTION_ACTIONS | NONPRODUCTION_ACTIONS):
        return stop("unknown DIS controlled action", "STOP_UNKNOWN_ACTION")
    if not _allowed_for_stage(state.get("active_stage"), action):
        return stop("action not permitted in active stage", "STOP_STAGE_ACTION_SCOPE")
    start = check_start_authorization(state, start_receipt, signing_key)
    if not start["allowed"]:
        return start
    execution = state["execution"]
    try:
        ledger = _read_pinned_json(root, execution.get("dec_ledger"))
        view = _pcs_view(state, execution)
        dec = validate_pre_execution(ledger, view, root)
        if not dec["allowed"]:
            return stop("; ".join(dec["errors"]), "STOP_DEC_001")
        checks = [{"id": "dec_pre", "status": "DEC_PRE_EXEC_PASS",
                   "evidence": execution["dec_ledger"]}]
        if state["active_stage"] in DISCOVERY or action in PRODUCTION_ACTIONS:
            rqc = _read_pinned_json(root, execution.get("rqc_ledger"))
            # RQC verifies actual file/sources in the provided checkout.
            research = validate_research(rqc, Path(root))
            if not research["allowed"]:
                return stop("; ".join(research["errors"]), "STOP_RQC_001")
            checks.append({"id": "rqc", "status": "RQC_STRUCTURE_READY",
                           "evidence": execution["rqc_ledger"]})
        if action in PRODUCTION_ACTIONS or action == "propose_art_direction":
            manifest = _read_pinned_json(root, execution.get("stg_manifest"))
            if (manifest.get("project") != execution["project"] or
                    manifest.get("scope") != _project_scope(state)):
                return stop("STG manifest belongs to another project/design scope",
                            "STOP_STG_SCOPE")
            expected_research = state["route"]["scopes"]["research"]
            recorded_research = manifest.get("research_scope", manifest.get("scope"))
            if recorded_research != expected_research:
                return stop("STG manifest does not declare approved Research Scope",
                            "STOP_STG_SCOPE")
            guard = check_stage_guard(manifest, action, root=root)
            if not guard["allowed"]:
                return stop(guard.get("reason", guard["code"]), "STOP_STG_001")
            checks.append({"id": "stg", "status": "STG_ALLOW",
                           "evidence": execution["stg_manifest"]})
        return {"allowed": True, "code": "READY_FOR_CONTROLLED_EXECUTION",
                "start_snapshot_sha256": start["start_snapshot_sha256"],
                "checks": checks, "warning":
                "Procedural/controlled-path gate only; direct native tools are outside."}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError,
            json.JSONDecodeError) as exc:
        return stop(str(exc), "STOP_EXECUTION_PREFLIGHT")


def review_stage_result(state, root, *, action, start_receipt, signing_key):
    """DEC's actual-artifact audit + stage acceptance; still not author SRA."""
    pre = review_execution(state, root, action=action,
                           start_receipt=start_receipt, signing_key=signing_key)
    if not pre["allowed"]:
        return pre
    ex = state["execution"]
    try:
        ledger = _read_pinned_json(root, ex["dec_ledger"])
        audit = _read_pinned_json(root, ex["artifact_audit"])
        artifact = ex.get("result_artifact")
        if not isinstance(artifact, str):
            return stop("missing result artifact")
        view = _pcs_view(state, ex)
        dec = audit_actual_artifact(ledger, view, root, artifact, audit)
        if not dec["allowed"]:
            return stop("; ".join(dec["errors"]), "STOP_DEC_ARTIFACT")
        current = copy.deepcopy(state)
        # On stage exit the exact reviewed gate identities must be part of
        # the snapshot that the author sees and signs.
        current["review_gates"] = {
            "start_snapshot_sha256": pre["start_snapshot_sha256"],
            "checks": pre["checks"],
            "result_artifact": {"path": artifact,
                                "sha256": dec["artifact_sha256"]},
            "dec_audit": ex["artifact_audit"],
            "review_state": "READY_FOR_AUTHOR_REVIEW",
        }
        exit_check = stage_exit(current, root)
        if not exit_check["allowed"]:
            return {"allowed": False, "code": exit_check["code"],
                    "summary": exit_check.get("summary"),
                    "blocking": exit_check.get("blocking", [])}
        return {"allowed": True, "code": "STAGE_REVIEW_READY_NOT_APPROVED",
                "review_state": current,
                "exit_summary": exit_check["summary"],
                "warning": "Human artistic/research acceptance remains separate."}
    except (OSError, ValueError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        return stop(str(exc), "STOP_STAGE_RESULT")


def transition_request(github, repo, root, *, branch="main",
                       signing_key=None):
    """Official next-stage command: a verified exit request, not an SRA/SSA."""
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    state = loaded["state"]
    result = request_next_stage(state, root)
    if result["code"] == "PREPARE_NEXT_STAGE_PACKET_ONLY":
        if not signing_key:
            return stop("trusted approval issuer not connected",
                        "STOP_APPROVAL_HISTORY_UNVERIFIED")
        history = state.get("history", [])
        gates = state.get("review_gates")
        if not history or not isinstance(gates, dict):
            return stop("approved stage without verified gate/receipt",
                        "STOP_APPROVAL_HISTORY_UNVERIFIED")
        approved = history[-1]
        # Check the exact snapshot as it existed before the final promotion.
        review = copy.deepcopy(state)
        review["stage_status"] = "READY_FOR_AUTHOR_REVIEW"
        snapshot = stage_exit(review, root)
        if not snapshot.get("allowed"):
            return stop("approved evidence is missing or stale",
                        "STOP_APPROVAL_HISTORY_UNVERIFIED")
        digest = snapshot["summary"]["snapshot_sha256"]
        receipt = approved.get("approval_receipt")
        verified = verify_approval(
            digest, receipt, "stage_result", state["active_stage"],
            _project_scope(state), signing_key,
        )
        if (not verified["allowed"] or
                approved.get("result_snapshot_sha256") != digest or
                approved.get("stage") != state["active_stage"] or
                approved.get("version") != state["stage_version"]):
            return stop("previous stage SRA invalid or stale",
                        "STOP_APPROVAL_HISTORY_UNVERIFIED")
        return {"allowed": True, "code": "PREPARE_NEXT_STAGE_PACKET_ONLY",
                "start_requires_separate_SSA": True}
    return result


def publish_approved_stage(github, repo, reviewed_state, receipt, signing_key,
                           root, *, action, start_receipt, branch="main"):
    """Re-run all checks against current GitHub state and exact reviewed hash.

    This is the sole supported promotion path. No approval means no write.
    """
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    state = loaded["state"]
    if state["stage_status"] == "APPROVED":
        return stop("stage already approved")
    fresh = review_stage_result(state, root, action=action,
                                start_receipt=start_receipt,
                                signing_key=signing_key)
    if not fresh["allowed"]:
        return fresh
    current_review = fresh["review_state"]
    if (reviewed_state.get("review_gates") != current_review["review_gates"] or
            reviewed_state.get("route") != current_review["route"] or
            reviewed_state.get("decisions") != current_review["decisions"] or
            reviewed_state.get("acceptance_criteria") != current_review["acceptance_criteria"] or
            reviewed_state.get("stage_version") != current_review["stage_version"]):
        return stop("review evidence changed since the operator saw the result",
                    "STOP_STALE_STAGE_REVIEW")
    if (stage_exit(reviewed_state, root).get("summary", {}).get("snapshot_sha256") !=
            fresh["exit_summary"]["snapshot_sha256"]):
        return stop("reviewed stage snapshot differs from fresh result",
                    "STOP_STALE_STAGE_REVIEW")
    checked = verify_author_stage_approval(current_review, receipt,
                                           signing_key, root)
    if not checked["allowed"]:
        return checked
    # Gateway adapter separately verifies PCS receipt and GitHub CAS/readback.
    return commit_state(github, loaded, checked["candidate_state"],
                        approval_key=signing_key)



def propose_next_stage(github, repo, root, acceptance_criteria, *,
                       branch="main", signing_key=None):
    """Prepare a precise SSA packet. No automatic start or GitHub change."""
    verified = transition_request(github, repo, root, branch=branch,
                                  signing_key=signing_key)
    if not verified["allowed"] or verified["code"] != "PREPARE_NEXT_STAGE_PACKET_ONLY":
        return verified
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    state = loaded["state"]
    plan = (state["route"]["stage_plan"] if state.get("route") else
            ["bootstrap", "intake", "project_configuration"])
    current = state["active_stage"]
    if current not in plan or plan.index(current) == len(plan) - 1:
        return stop("no remaining stage in selected route")
    if (not isinstance(acceptance_criteria, list) or
            not acceptance_criteria or
            any(not isinstance(r, dict) or not r.get("id") or
                r.get("class") not in ("REQUIRED", "JUDGEMENT", "OPTIONAL", "DEPENDENT")
                for r in acceptance_criteria)):
        return stop("next-stage acceptance criteria must be defined before SSA")
    new = copy.deepcopy(state)
    new["active_stage"] = plan[plan.index(current) + 1]
    new["stage_status"] = "IN_PROGRESS"
    new["stage_version"] = "v1"
    new["acceptance_criteria"] = copy.deepcopy(acceptance_criteria)
    new.pop("review_gates", None)
    new.pop("execution", None)
    new.pop("result_artifact", None)
    new.pop("start_receipt", None)
    packet_sha = _digest(_canonical(_start_payload(new)))
    return {
        "allowed": True,
        "code": "READY_FOR_SEPARATE_NEXT_SSA",
        "candidate_state": new,
        "next_stage": new["active_stage"],
        "stage_start_snapshot_sha256": packet_sha,
        "warning": "Author review/signing is required before this stage begins.",
    }


def activate_next_stage(github, repo, candidate_state, start_receipt,
                        approval_key, start_key, *, branch="main"):
    """Author-approved SSA permits only the very next stage; no production."""
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    proposed = copy.deepcopy(candidate_state)
    proposed["start_receipt"] = copy.deepcopy(start_receipt)
    return commit_state(
        github, loaded, proposed,
        approval_key=approval_key, start_key=start_key,
    )



def propose_route_selection(github, repo, config, *, branch="main"):
    """Offer an author-reviewable, not-yet-selected route."""
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    state = loaded["state"]
    if (state["active_stage"] != "project_configuration" or
            state["stage_status"] != "IN_PROGRESS" or
            state.get("route") is not None):
        return stop("route selection is allowed only in initial project configuration")
    compiled = compile_route(config)
    if not compiled["allowed"]:
        return compiled
    proposed = copy.deepcopy(state)
    proposed["route"] = {
        **copy.deepcopy(config),
        "stage_plan": compiled["stage_plan"],
    }
    route_sha = _digest(_canonical({
        "project_repo": repo,
        "stage": "project_configuration",
        "stage_version": state["stage_version"],
        "route": proposed["route"],
    }))
    return {"allowed": True, "code": "ROUTE_AWAITING_AUTHOR_SELECTION",
            "candidate_state": proposed,
            "route_snapshot_sha256": route_sha,
            "alternatives_considered": True,
            "warning": "The recommendation is not an author's approval."}


def confirm_route_selection(github, repo, candidate_state, receipt,
                            trusted_route_key, *, branch="main"):
    """Commit only a separately signed operator-selected strategy and scopes."""
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    candidate = copy.deepcopy(candidate_state)
    candidate["route_approval_receipt"] = copy.deepcopy(receipt)
    return commit_state(github, loaded, candidate, route_key=trusted_route_key)



def record_alpha_operator_review(github, repo, root, *, stage_version,
                                 snapshot_sha256, operator_statement,
                                 branch="main"):
    """Record explicit but UNAUTHENTICATED Alpha review; never approve a stage.

    This provides a limited LLM-facing review log for the alpha trial.
    Actual protected stage promotion still requires independently signed SRA.
    """
    loaded = load_project(github, repo, branch)
    if not loaded["allowed"]:
        return loaded
    state = loaded["state"]
    if state["stage_status"] == "APPROVED":
        return stop("already approved stage requires no procedural review")
    if not isinstance(operator_statement, str) or not operator_statement.strip():
        return stop("explicit operator statement required")
    if not operator_statement.strip().casefold().startswith("утверждаю этап"):
        return stop("explicit 'Утверждаю этап' confirmation required")
    if state["stage_version"] != stage_version:
        return stop("operator reviewed a different stage version")
    checked = stage_exit(state, root)
    if not checked.get("allowed"):
        return stop("cannot record successful review while required checks fail")
    actual_snapshot = checked["summary"]["snapshot_sha256"]
    if snapshot_sha256 != actual_snapshot:
        return stop("reviewed snapshot changed or was not shown to operator")
    old = state.get("procedural_reviews", [])
    if not isinstance(old, list):
        return stop("invalid procedural review history")
    if any(x.get("snapshot_sha256") == actual_snapshot for x in old
           if isinstance(x, dict)):
        return stop("duplicate procedural review for exact snapshot")
    proposal = copy.deepcopy(state)
    proposal["procedural_reviews"] = old + [{
        "kind": "PROCEDURAL_REVIEW_ACCEPTED",
        "stage": state["active_stage"],
        "version": stage_version,
        "snapshot_sha256": actual_snapshot,
        "operator_statement": operator_statement.strip(),
        "identity_verified": False,
        "protected_stage_approval": False,
    }]
    # Never edit stage status to APPROVED in procedural mode.
    saved = commit_state(github, loaded, proposal)
    if not saved["allowed"]:
        return saved
    return {
        "allowed": True,
        "code": "ALPHA_REVIEW_RECORDED_NOT_APPROVED",
        "record_commit": saved["commit"],
        "stage_status": state["stage_status"],
        "warning": "GitHub entry exists but is NOT authenticated SRA/SSA. "
                   "Protected stage progression remains blocked.",
    }
