"""Dependency impact analysis and evidence-grounded export gates.

These are deterministic preflight helpers, not artifact generators.
"""
from collections import deque
from pathlib import Path
import hashlib
from tools.enforcement.pcs_controller import verify_approval

# Important: dependencies are *data per project*, not assumed to be a
# universal linear chain. Explicitly track links among actual artifacts.


def affected_by_revision(stage_id, dependencies, approved_stages):
    """List accepted descendants of a revised stage; never auto-unapprove them."""
    if stage_id not in dependencies:
        return {"allowed": False, "code": "STOP_UNKNOWN_STAGE"}
    reverse = {}
    for child, parents in dependencies.items():
        if not isinstance(parents, list):
            return {"allowed": False, "code": "STOP_INVALID_DEPENDENCIES"}
        for parent in parents:
            if parent not in dependencies:
                return {"allowed": False, "code": "STOP_INVALID_DEPENDENCIES"}
            reverse.setdefault(parent, set()).add(child)
    result, seen = [], {stage_id}
    queue = deque([stage_id])
    while queue:
        current = queue.popleft()
        for child in sorted(reverse.get(current, ())):
            if child not in seen:
                seen.add(child)
                queue.append(child)
                if child in approved_stages:
                    result.append(child)
    return {"allowed": True, "code": "REVISION_IMPACT_ANALYZED",
            "revised_stage": stage_id,
            "requires_revalidation": result,
            "status_change_applied": False}


def verify_final_artifacts(root, requested, artifacts, decisions, signing_key=None):
    """Ensure every chosen deliverable is linked to real stage evidence.

    Prevents retrospective invented rationale, missing files and unchecked
    optional outputs. Source references must identify actual registered
    decision IDs. An approved output requires a verified SRA receipt, not a self-declared flag.\n    Even PASS cannot attest visual/semantic truth.
    """
    root = Path(root).resolve()
    errors = []
    if not isinstance(requested, list) or not requested:
        return {"allowed": False, "code": "STOP_DELIVERY", "errors": ["no requested documents"]}
    if not isinstance(artifacts, list) or not isinstance(decisions, list):
        return {"allowed": False, "code": "STOP_DELIVERY", "errors": ["bad artifact or decision register"]}
    ids = {d.get("id") for d in decisions if isinstance(d, dict) and d.get("id")}
    index = {a.get("id"): a for a in artifacts if isinstance(a, dict) and a.get("id")}
    for item in requested:
        if item not in index:
            errors.append("missing requested artifact: " + str(item))
            continue
        record = index[item]
        path = record.get("path")
        expected_sha = record.get("sha256")
        if not isinstance(path, str) or not path or Path(path).is_absolute():
            errors.append(str(item) + ": unsafe/missing path")
            continue
        file = (root / path).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            errors.append(str(item) + ": no actual file")
            continue
        if (not isinstance(expected_sha, str) or
                hashlib.sha256(file.read_bytes()).hexdigest() != expected_sha):
            errors.append(str(item) + ": stale artifact bytes")
        refs = record.get("decision_ids")
        if not isinstance(refs, list) or not refs:
            errors.append(str(item) + ": missing rationale provenance")
        elif any(ref not in ids for ref in refs):
            errors.append(str(item) + ": unsupported decision citation")
        receipt = record.get("approval_receipt")
        snapshot = record.get("result_snapshot_sha256")
        stage = record.get("stage")
        scope = record.get("scope")
        checked = verify_approval(
            snapshot, receipt, "stage_result", stage, scope, signing_key
        ) if all(isinstance(v, str) and v for v in (snapshot, stage, scope)) else {
            "allowed": False, "code": "STOP_APPROVAL_SOURCE_MISSING"
        }
        if not checked["allowed"]:
            errors.append(str(item) + ": no independent stage SRA: " + checked["code"])
    return {"allowed": not errors,
            "code": "DELIVERY_EVIDENCE_AUTHORIZED_NOT_VISUALLY_CERTIFIED" if not errors else "STOP_DELIVERY",
            "errors": errors,
            "warning": "File/ledger integrity is not independent human approval or graphic quality."}
