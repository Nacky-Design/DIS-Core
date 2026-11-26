#!/usr/bin/env python3
"""DEC-001 fail-closed requirement/plan/artifact gate for controlled execution paths.

This checks structured evidence and coverage, NOT whether a model actually
read and understood all prose, NOT visual/artistic truth and NOT a tool
interceptor. Integrate this check into any controlled creative production tool
route; direct ChatGPT / Figma tools remain outside this gate until connected.
"""
import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "DEC-001/v1"
STOP = "STOP_DEC_001"
REQUIREMENT_FIELDS = (
    "id", "source_id", "source_path", "source_sha256", "source_anchor",
    "approval_state", "scope", "lock", "criterion", "implementation_plan",
    "verification_kind", "severity",
)
FAKE_PLANS = {
    "учтено", "соблюдено", "реализовано", "готово", "todo", "tbd",
    "see prompt", "see docs", "следуем документам", "выполнено",
    "по умолчанию", "смотри промпт", "соответствует",
}
APPROVED = "approved_by_user"
LOCK_VALUES = {"LOCKED", "GUIDED", "OPEN"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_file(root, path):
    if not isinstance(path, str) or not path or Path(path).is_absolute():
        raise ValueError("Invalid relative path")
    base = Path(root).resolve()
    target = (base / path).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError("Missing or unsafe path: " + path)
    return target


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _bad_plan(value):
    if not _text(value):
        return True
    normalized = " ".join(value.strip().casefold().split())
    return normalized in FAKE_PLANS or len(normalized) < 28


def validate_pre_execution(ledger, manifest, root):
    errors = []
    if not isinstance(ledger, dict) or ledger.get("schema") != SCHEMA:
        return {"allowed": False, "code": STOP, "errors": ["invalid DEC schema"]}
    if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list):
        return {"allowed": False, "code": STOP, "errors": ["invalid PCS source inventory"]}
    for field in ("project", "stage_id", "scope"):
        if ledger.get(field) != manifest.get(field):
            errors.append("scope mismatch: " + field)
    prompt = manifest.get("prompt", {})
    if ledger.get("stage_prompt_sha256") != prompt.get("sha256"):
        errors.append("stale stage prompt hash")
    if not _text(ledger.get("pcs_snapshot_sha256")):
        errors.append("missing verified PCS snapshot identity")
    if not _text(ledger.get("execution_plan")) or _bad_plan(ledger.get("execution_plan")):
        errors.append("missing concrete overall production plan")

    source_index = {s.get("id"): s for s in manifest["sources"] if isinstance(s, dict)}
    for source_id, source in source_index.items():
        try:
            current = digest(safe_file(root, source.get("path")).read_bytes())
            if current != source.get("sha256"):
                errors.append("stale source: " + str(source_id))
        except (OSError, ValueError, TypeError) as exc:
            errors.append("unreadable source " + str(source_id) + ": " + str(exc))
    try:
        if digest(safe_file(root, prompt.get("path")).read_bytes()) != prompt.get("sha256"):
            errors.append("stale prompt bytes")
    except (OSError, ValueError, TypeError) as exc:
        errors.append("unreadable prompt: " + str(exc))

    requirements = ledger.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        return {"allowed": False, "code": STOP,
                "errors": errors + ["missing requirement ledger"]}
    ids = set()
    mapped = set()
    for r in requirements:
        if not isinstance(r, dict):
            errors.append("invalid requirement record")
            continue
        rid = r.get("id")
        if not _text(rid):
            errors.append("requirement has no id")
            continue
        if rid in ids:
            errors.append("duplicate requirement id: " + rid)
        ids.add(rid)
        missing = [key for key in REQUIREMENT_FIELDS if not _text(r.get(key))]
        if missing:
            errors.append(rid + ": missing fields: " + ", ".join(missing))
            continue
        source = source_index.get(r["source_id"])
        if not source or r["source_path"] != source.get("path") or r["source_sha256"] != source.get("sha256"):
            errors.append(rid + ": unknown/stale source")
        if r["scope"] not in (manifest.get("scope"), "*", "GLOBAL"):
            errors.append(rid + ": wrong scope")
        if r["lock"] not in LOCK_VALUES:
            errors.append(rid + ": invalid LOCKED/GUIDED/OPEN")
        if r["approval_state"] != (source or {}).get("status"):
            errors.append(rid + ": source approval status mismatch")
        if _bad_plan(r["implementation_plan"]):
            errors.append(rid + ": absent/generic implementation mapping")
        if len(r["criterion"].strip()) < 15:
            errors.append(rid + ": criterion is not testable")
        if r["verification_kind"] not in ("mechanical", "visual", "editorial", "functional", "manual"):
            errors.append(rid + ": unknown verification mode")
        if r["severity"] not in ("critical", "major", "minor"):
            errors.append(rid + ": unknown severity")
        mapped.add(rid)
    # Every applicable approved PCS decision ID must have an implementation mapping.
    for decision in manifest.get("decisions", []):
        if not isinstance(decision, dict):
            errors.append("invalid decision")
            continue
        if decision.get("status") == APPROVED and decision.get("scope") in (manifest.get("scope"), "*", "GLOBAL"):
            ident = decision.get("id")
            if ident not in mapped:
                errors.append("unmapped approved decision: " + str(ident))
            elif not any(r.get("id") == ident and r.get("source_id") == decision.get("source_id") and
                         r.get("lock") == decision.get("lock") for r in requirements if isinstance(r, dict)):
                errors.append("decision source/lock mismatch: " + str(ident))
    # Explicit evidence for every approved predecessor source, including UI Kit and prototype.
    covered = ledger.get("source_coverage", [])
    if not isinstance(covered, list):
        covered = []
        errors.append("invalid source coverage")
    for source_id, source in source_index.items():
        if source.get("status") == APPROVED and not any(
            isinstance(c, dict) and c.get("source_id") == source_id and
            c.get("source_sha256") == source.get("sha256") and
            _text(c.get("extraction_evidence")) for c in covered
        ):
            errors.append("unverified approved source extraction: " + source_id)
    for record in ledger.get("conflicts", []):
        if not isinstance(record, dict) or record.get("status") != "resolved" or not _text(record.get("approval_ref")):
            errors.append("unresolved/unapproved requirement conflict")
    if ledger.get("source_coverage_complete") is not True:
        errors.append("source extraction completeness not attested")
    if ledger.get("pre_execution", {}).get("status") != "PASS":
        errors.append("pre-execution evidence not marked PASS")
    if not _text(ledger.get("pre_execution", {}).get("evidence")):
        errors.append("pre-execution evidence missing")
    return {"allowed": not errors, "code": "DEC_PRE_EXEC_PASS" if not errors else STOP,
            "errors": errors, "mapped_requirements": len(mapped)}


def audit_actual_artifact(ledger, manifest, root, artifact_path, audit):
    pre = validate_pre_execution(ledger, manifest, root)
    if not pre["allowed"]:
        return pre
    errors = []
    try:
        artifact_sha = digest(safe_file(root, artifact_path).read_bytes())
    except (OSError, ValueError, TypeError) as exc:
        return {"allowed": False, "code": "REJECTED", "errors": ["artifact unreadable: " + str(exc)]}
    if not isinstance(audit, dict) or audit.get("artifact_sha256") != artifact_sha:
        return {"allowed": False, "code": "REJECTED", "errors": ["missing/stale actual artifact evidence"]}
    checks = audit.get("checks")
    if not isinstance(checks, list):
        return {"allowed": False, "code": "REJECTED", "errors": ["missing artifact checks"]}
    check_index = {r.get("id"): r for r in checks if isinstance(r, dict)}
    for r in ledger["requirements"]:
        ident = r["id"]
        check = check_index.get(ident)
        if not check:
            errors.append("unchecked artifact requirement: " + ident)
            continue
        status = check.get("status")
        if status not in ("PASS", "FAIL", "NOT_CHECKED"):
            errors.append("unknown QA status: " + ident)
        if not _text(check.get("evidence")) or not _text(check.get("artifact_ref")):
            errors.append("no observed artifact evidence: " + ident)
        if r.get("severity") == "critical" and status != "PASS":
            errors.append("critical requirement failed/unverified: " + ident)
    return {"allowed": not errors, "code": "READY_FOR_SEPARATE_SRA" if not errors else "REJECTED",
            "artifact_sha256": artifact_sha, "errors": errors,
            "warning": "Recorded QA evidence is not an independently verified art judgment or user approval."}


def main():
    cli = argparse.ArgumentParser(description="DEC-001 pre-execution requirement mapping validator")
    cli.add_argument("--manifest", required=True)
    cli.add_argument("--ledger", required=True)
    cli.add_argument("--root", required=True)
    cli.add_argument("--artifact")
    cli.add_argument("--audit")
    args = cli.parse_args()
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
        if args.artifact or args.audit:
            if not args.artifact or not args.audit:
                result = {"allowed": False, "code": "REJECTED", "errors": ["artifact/audit pair required"]}
            else:
                audit = json.loads(Path(args.audit).read_text(encoding="utf-8"))
                result = audit_actual_artifact(ledger, manifest, args.root, args.artifact, audit)
        else:
            result = validate_pre_execution(ledger, manifest, args.root)
    except (OSError, ValueError) as exc:
        result = {"allowed": False, "code": STOP, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("allowed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
