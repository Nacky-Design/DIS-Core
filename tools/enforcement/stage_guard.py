#!/usr/bin/env python3
"""DIS stage guard: fail-closed stage transition check for controlled tool routes.

Never an interceptor for native ChatGPT or Figma calls. RQC is a STRUCTURAL
evidence check, not an independent assessment of actual research quality.
"""
import argparse
import json
import pathlib
import sys

from tools.enforcement.research_quality_gate import validate as validate_research

GATES = ("intake", "research_ux", "prototype", "references", "art_direction", "ui_kit")
PRODUCTION = {"visual_concept", "image_generation", "figma_write", "html_production"}
RESEARCH = {"research_report", "research_review"}
ART_PROPOSAL = {"propose_art_direction"}
STATUS_OK = {"approved_by_user"}
LOCAL = {"local_refinement"}
STOP = "STOP_STAGE_VIOLATION"


def _research_check(data, root):
    path = data.get("research_quality_ledger")
    if not isinstance(path, str) or not path.strip():
        return {"allowed": False, "code": "STOP_DISCOVERY_INCOMPLETE",
                "reason": "missing RQC-001 evidence ledger"}
    try:
        base = pathlib.Path(root).resolve()
        file = (base / path).resolve()
        if pathlib.Path(path).is_absolute() or not file.is_relative_to(base) or not file.is_file():
            raise ValueError("unsafe/missing RQC evidence ledger")
        ledger = json.loads(file.read_text(encoding="utf-8"))
        # v2 keeps Research Scope independent from Design Scope; legacy
        # manifests continue using their original single "scope" field.
        expected_research_scope = data.get("research_scope", data["scope"])
        if (ledger.get("project") != data["project"] or
                ledger.get("scope") != expected_research_scope):
            return {"allowed": False, "code": "STOP_DISCOVERY_INCOMPLETE",
                    "reason": "research project/scope mismatch"}
        verdict = validate_research(ledger, base)
        if not verdict["allowed"]:
            return {"allowed": False, "code": "STOP_DISCOVERY_INCOMPLETE",
                    "reason": "RQC failed", "errors": verdict["errors"]}
        return verdict
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        return {"allowed": False, "code": "STOP_DISCOVERY_INCOMPLETE",
                "reason": str(exc)}


def check(data, action, root="."):
    if action not in PRODUCTION | LOCAL | RESEARCH | ART_PROPOSAL:
        return {"allowed": False, "code": "UNKNOWN_ACTION"}
    if not isinstance(data, dict):
        return {"allowed": False, "code": STOP, "reason": "missing project manifest"}
    if not data.get("project") or not data.get("scope"):
        return {"allowed": False, "code": STOP, "reason": "project and scope required"}
    if data.get("mode") == "local_correction":
        baseline = data.get("baseline")
        if action != "local_refinement":
            return {"allowed": False, "code": STOP, "reason": "local fast-track cannot create a new concept"}
        if not isinstance(baseline, dict) or not all(baseline.get(k) for k in ("path", "sha256", "approval_ref", "protected_scope")):
            return {"allowed": False, "code": STOP, "reason": "approved baseline evidence required"}
        # A boolean is not independent proof of a human approval.
        if baseline.get("approval_verified") is not True:
            return {"allowed": False, "code": STOP, "reason": "baseline approval not verified"}
        return {"allowed": True, "code": "ALLOW_LOCAL_REFINEMENT",
                "warning": "Approval attestations still need external verification."}
    if action == "local_refinement":
        return {"allowed": False, "code": STOP, "reason": "local refinement requires an approved baseline"}

    research = _research_check(data, root)
    if not research["allowed"]:
        return research

    if action in RESEARCH:
        return {"allowed": True, "code": "READY_FOR_HUMAN_RESEARCH_REVIEW",
                "warning": "RQC checks coverage/integrity only; this is NOT research approval or an editorial PASS."}

    gates = data.get("gates")
    if not isinstance(gates, dict):
        return {"allowed": False, "code": STOP, "reason": "no gates in manifest"}
    required = ("intake", "research_ux", "prototype", "references") if action in ART_PROPOSAL else GATES
    for gate in required:
        item = gates.get(gate)
        if not isinstance(item, dict):
            return {"allowed": False, "code": STOP, "reason": "gate missing: " + gate}
        if item.get("status") not in STATUS_OK:
            return {"allowed": False, "code": STOP, "reason": "gate not approved: " + gate}
        if not isinstance(item.get("evidence"), list) or not item["evidence"]:
            return {"allowed": False, "code": STOP, "reason": "gate evidence missing: " + gate}
        if not item.get("approval_ref") or item.get("approval_verified") is not True:
            return {"allowed": False, "code": STOP, "reason": "gate human approval unverified: " + gate}
    if action in ART_PROPOSAL:
        return {"allowed": True, "code": "ALLOW_ART_DIRECTION_PROPOSAL",
                "warning": "Approval attestations require independent audit; AD selection is still human."}
    return {"allowed": True, "code": "ALLOW",
            "warning": "Approval attestations require independent external audit."}


def main():
    parser = argparse.ArgumentParser(description="DIS fail-closed stage + research preflight")
    parser.add_argument("--manifest", required=True, type=pathlib.Path)
    parser.add_argument("--action", required=True)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = check(manifest, args.action, root=args.root)
    except (OSError, ValueError) as exc:
        result = {"allowed": False, "code": STOP, "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    sys.exit(main())
