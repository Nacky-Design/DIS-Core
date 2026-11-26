"""GitHub state persistence boundary for DIS v2.

Injected GitHub client implements:
    read(repo, path, branch) -> {'content': UTF8 string, 'sha': blob_sha, 'commit': branch_sha}
    write(repo, path, branch, content, expected_blob_sha) -> {'commit': commit_sha}
The adapter only verifies readback and expected branch/file identity. A plain
connection with write permissions is NOT a privileged user-approval issuer.
"""
import json
from tools.enforcement.dis_project_v2 import (
    SCHEMA, _canonical, _digest, _exit_payload, _start_payload, validate_state
)
from tools.enforcement.pcs_controller import verify_approval

STATE_FILE = ".dis/project-state.json"


def _stop(reason):
    return {"allowed": False, "code": "STOP_PROJECT_STATE", "reason": reason}


def load_project(github, repository, branch="main"):
    """Never synthesize APPROVED or recover from chat if remote read fails."""
    try:
        value = github.read(repository, STATE_FILE, branch)
        if not isinstance(value, dict) or not isinstance(value.get("sha"), str):
            return _stop("unverified GitHub read / missing file identity")
        text = value["content"]
        parsed = json.loads(text)
        check = validate_state(parsed)
        if not check["allowed"]:
            return _stop("invalid GitHub project state: " + "; ".join(check["errors"]))
        if parsed["project_repo"] != repository:
            return _stop("state points to another repository")
        return {"allowed": True, "code": "REMOTE_STATE_LOADED",
                "state": parsed, "blob_sha": value["sha"],
                "remote_commit": value.get("commit"),
                "repository": repository, "branch": branch}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as exc:
        return _stop("GitHub remote read failed: " + str(exc))


def commit_state(github, loaded_state, proposed_state, approval_key=None,
                 start_key=None, route_key=None):
    """Compare-and-swap then GitHub readback. Never self-approve.

    Must be called only AFTER independent authorization has produced
    proposed_state. It verifies PCS receipt with a separately provided privileged issuer key
    for status promotion; the transport is NOT a tool gateway.
    """
    if not isinstance(loaded_state, dict) or not loaded_state.get("allowed"):
        return _stop("verified remote starting state is required")
    repo = loaded_state.get("repository")
    branch = loaded_state.get("branch")
    blob_sha = loaded_state.get("blob_sha")
    if not all(isinstance(x, str) and x for x in (repo, branch, blob_sha)):
        return _stop("missing repository, branch or expected blob SHA")
    check = validate_state(proposed_state)
    if not check["allowed"]:
        return _stop("proposed state invalid: " + "; ".join(check["errors"]))
    if proposed_state["project_repo"] != repo:
        return _stop("cross-repository state write")
    original = loaded_state["state"]
    if proposed_state.get("methodology_revision") != original.get("methodology_revision"):
        return _stop("methodology revision changes require separate migration approval")
    if proposed_state.get("history") != original.get("history") and not (
        original.get("stage_status") != "APPROVED" and
        proposed_state.get("stage_status") == "APPROVED"
    ):
        return _stop("history is immutable outside signed stage approval")

    route_changed = proposed_state.get("route") != original.get("route")
    if route_changed:
        if (original.get("active_stage") != "project_configuration" or
                original.get("stage_status") == "APPROVED" or
                original.get("route") is not None or
                not route_key):
            return _stop("route change requires independent configuration approval")
        route_value = dict(proposed_state["route"])
        route_receipt = proposed_state.get("route_approval_receipt")
        route_snapshot = _digest(_canonical({
            "project_repo": repo,
            "stage": "project_configuration",
            "stage_version": original["stage_version"],
            "route": route_value,
        }))
        checked_route = verify_approval(
            route_snapshot, route_receipt, "project_route",
            "project_configuration", "route", route_key
        )
        if not checked_route["allowed"]:
            return _stop("route authorization invalid: " + checked_route["code"])
        # A route confirmation may not smuggle unrelated changes in one commit.
        old_fields = dict(original)
        new_fields = dict(proposed_state)
        for key in ("route", "route_approval_receipt"):
            old_fields.pop(key, None)
            new_fields.pop(key, None)
        if old_fields != new_fields:
            return _stop("route confirmation attempted unrelated state changes")

    stage_changed = proposed_state.get("active_stage") != original.get("active_stage")
    if not stage_changed and not route_changed and (
        _start_payload(proposed_state) != _start_payload(original)
    ):
        return _stop("stage start contract changed; revised author SSA required")
    if stage_changed:
        if original.get("stage_status") != "APPROVED":
            return _stop("cannot advance an unapproved stage")
        if not approval_key or not start_key:
            return _stop("both previous SRA and next SSA issuers are required")
        history = original.get("history", [])
        if not history or history[-1].get("stage") != original["active_stage"]:
            return _stop("missing previous-stage approved history")
        last = history[-1]
        previous_snapshot = _digest(_canonical(_exit_payload(original)))
        if last.get("result_snapshot_sha256") != previous_snapshot:
            return _stop("previous SRA snapshot is stale")
        prev_sra = verify_approval(
            previous_snapshot, last.get("approval_receipt"), "stage_result",
            original["active_stage"],
            (original["route"]["scopes"]["design"] if original.get("route")
             else "bootstrap"), approval_key
        )
        if not prev_sra["allowed"]:
            return _stop("previous SRA cannot be verified: " + prev_sra["code"])
        plan = (original["route"]["stage_plan"] if original.get("route") else
                ["bootstrap", "intake", "project_configuration"])
        current = original["active_stage"]
        if current not in plan or plan.index(current) + 1 >= len(plan):
            return _stop("no eligible next stage")
        if proposed_state["active_stage"] != plan[plan.index(current) + 1]:
            return _stop("attempt to skip a stage")
        if proposed_state["stage_status"] != "IN_PROGRESS":
            return _stop("next stage must start IN_PROGRESS")
        if not proposed_state.get("acceptance_criteria"):
            return _stop("next stage must have pre-agreed acceptance criteria")
        if proposed_state.get("route") != original.get("route"):
            return _stop("stage advancement cannot silently change route")
        if proposed_state.get("decisions") != original.get("decisions"):
            return _stop("stage advancement cannot silently change decisions")
        if proposed_state.get("history") != original.get("history"):
            return _stop("stage advancement cannot rewrite history")
        if proposed_state.get("review_gates"):
            return _stop("new stage cannot inherit old review gate")
        next_sha = _digest(_canonical(_start_payload(proposed_state)))
        checked_start = verify_approval(
            next_sha, proposed_state.get("start_receipt"), "stage_start",
            proposed_state["active_stage"],
            (proposed_state["route"]["scopes"]["design"]
             if proposed_state.get("route") else "bootstrap"), start_key
        )
        if not checked_start["allowed"]:
            return _stop("next SSA invalid: " + checked_start["code"])
    elif original.get("stage_status") == "APPROVED":
        if proposed_state != original:
            return _stop("approved baseline is immutable without verified next-stage SSA")
    elif proposed_state.get("stage_status") == "APPROVED":
        # Signed promotion verification is performed below.
        pass
    elif proposed_state.get("stage_status") not in (
        "IN_PROGRESS", "NEEDS_WORK", "BLOCKED", "READY_FOR_AUTHOR_REVIEW", "PENDING_SAVE"
    ):
        return _stop("invalid draft state transition")
    if (proposed_state.get("stage_status") == "APPROVED" and
            loaded_state["state"].get("stage_status") != "APPROVED"):
        history = proposed_state.get("history", [])
        previous = loaded_state["state"].get("history", [])
        if len(history) != len(previous) + 1:
            return _stop("new approved state must contain exactly one approval event")
        record = history[-1]
        receipt = record.get("approval_receipt")
        if not approval_key:
            return _stop("independent approval issuer key not connected")
        # Only gate evidence and one approval event may be added during SRA.
        # All other state fields must exactly match the remote version.
        old_base = dict(loaded_state["state"])
        new_base = dict(proposed_state)
        for key in ("stage_status", "history", "review_gates"):
            old_base.pop(key, None)
            new_base.pop(key, None)
        if old_base != new_base:
            return _stop("approved update contains unauthorized changes to stage/route/decisions")
        if previous != history[:-1]:
            return _stop("approval history was modified")
        gates = proposed_state.get("review_gates")
        if not isinstance(gates, dict) or gates.get("review_state") != "READY_FOR_AUTHOR_REVIEW":
            return _stop("verified stage review gate record missing")
        reviewed_base = dict(loaded_state["state"])
        reviewed_base["review_gates"] = gates
        expected_snapshot = _digest(_canonical(_exit_payload(reviewed_base)))
        if record.get("result_snapshot_sha256") != expected_snapshot:
            return _stop("approval snapshot does not match the reviewed remote result")
        approval = verify_approval(
            expected_snapshot, receipt, "stage_result",
            loaded_state["state"]["active_stage"],
            loaded_state["state"]["route"]["scopes"]["design"], approval_key,
        )
        if not approval["allowed"]:
            return _stop("approval signature verification failed: " + approval["code"])
    raw = _canonical(proposed_state)
    try:
        # Re-read expected blob SHA immediately before the write, to fail
        # clearly if the project changed concurrently.
        current = github.read(repo, STATE_FILE, branch)
        if current["sha"] != blob_sha:
            return _stop("stale remote project state — compare-and-swap conflict")
        write = github.write(repo, STATE_FILE, branch, raw, blob_sha)
        if not isinstance(write, dict) or not write.get("commit"):
            return _stop("GitHub write returned no commit identity")
        after = github.read(repo, STATE_FILE, branch)
        if after.get("content") != raw:
            return _stop("GitHub readback does not match saved bytes")
        if json.loads(after["content"]) != proposed_state:
            return _stop("GitHub roundtrip mismatch")
        return {"allowed": True, "code": "GITHUB_READBACK_VERIFIED",
                "commit": write["commit"], "blob_sha": after.get("sha"),
                "stage_status": proposed_state["stage_status"]}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as exc:
        return _stop("GitHub state write/readback failed: " + str(exc))


def initialize_project(github, repository, state, branch="main"):
    """Create a brand-new GitHub project record, never infer an approved stage.

    Intended after the operator created an empty private repository. Route may
    legitimately be unselected; the operator will choose it at configuration.
    """
    if not isinstance(state, dict):
        return _stop("initial state missing")
    checked = validate_state(state)
    if not checked["allowed"]:
        return _stop("invalid initial project state: " + "; ".join(checked["errors"]))
    if state["project_repo"] != repository:
        return _stop("project repo name mismatch")
    if (state.get("active_stage") != "bootstrap" or
            state.get("stage_status") != "IN_PROGRESS" or
            state.get("route") is not None or state.get("history")):
        return _stop("new project must begin at unapproved bootstrap with no route")
    try:
        github.read(repository, STATE_FILE, branch)
        return _stop("project state already exists; use recovery, not initialization")
    except FileNotFoundError:
        pass
    except (OSError, ValueError, RuntimeError) as exc:
        return _stop("cannot verify empty project state: " + str(exc))
    try:
        raw = _canonical(state)
        result = github.create(repository, STATE_FILE, branch, raw)
        if not result or not result.get("commit"):
            return _stop("initial GitHub creation returned no commit")
        checked = load_project(github, repository, branch)
        if not checked["allowed"] or checked["state"] != state:
            return _stop("new project GitHub readback verification failed")
        return {"allowed": True, "code": "PROJECT_INITIALIZED_UNAPPROVED",
                "commit": result["commit"], "blob_sha": checked["blob_sha"],
                "status": "IN_PROGRESS"}
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        return _stop("GitHub project initialization failed: " + str(exc))
