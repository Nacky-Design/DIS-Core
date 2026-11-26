#!/usr/bin/env python3
"""RQC-001: fail-closed STRUCTURAL evidence gate for a Discovery first pass.

A green result means the report, source snapshots and critical self-review
have the required traceability. It does NOT independently prove research
quality, market truth, user insight, or human approval. A separate editorial
review and SRA-001 are still required.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SCHEMA = "RQC-001/v1"
STOP = "STOP_DISCOVERY_INCOMPLETE"
DIMENSIONS = {
    "business_context": 1,
    "audience_segments": 2,
    "jtbd": 2,
    "market_alternatives": 2,
    "customer_journey": 3,
    "decision_barriers": 2,
    "market_tensions": 1,
    "brand_capabilities": 1,
    "strategic_opportunities": 2,
    "validation_plan": 1,
}
AUDIT_CHECKS = (
    "source_coverage", "segment_and_jtbd", "alternatives_and_substitutes",
    "journey_and_barriers", "hypothesis_falsifiability", "contradictions_and_limits",
)
EVIDENCE_LEVELS = {"client_fact", "observed", "inference", "hypothesis"}
SOURCE_KINDS = {"client", "direct_competitor", "substitute", "market", "interview", "other"}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _text(value, minimum=1):
    return isinstance(value, str) and len(value.strip()) >= minimum


def safe_file(root, path):
    if not _text(path) or Path(path).is_absolute():
        raise ValueError("Missing or absolute path")
    base = Path(root).resolve()
    target = (base / path).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError("Missing or unsafe file: " + path)
    return target


def _read_pinned(root, record, label, errors):
    if not isinstance(record, dict):
        errors.append(label + ": expected file record")
        return None
    try:
        raw = safe_file(root, record.get("path")).read_bytes()
        if sha256(raw) != record.get("sha256"):
            errors.append(label + ": SHA256 mismatch")
            return None
        return raw
    except (OSError, ValueError, TypeError) as exc:
        errors.append(label + ": " + str(exc))
        return None


def validate(ledger, root):
    """Check evidence coverage before presenting Discovery as review-ready.

    This gate deliberately does NOT award a numeric 'research quality' score.
    No model-generated self-review can replace an independent human decision.
    """
    errors = []
    if not isinstance(ledger, dict) or ledger.get("schema") != SCHEMA:
        return {"allowed": False, "code": STOP, "errors": ["invalid RQC schema"]}
    for field in ("project", "scope"):
        if not _text(ledger.get(field)):
            errors.append("missing " + field)
    if ledger.get("stage") != "discovery":
        errors.append("RQC applies to discovery stage only")

    report_raw = _read_pinned(root, ledger.get("report"), "discovery report", errors)
    report_text = ""
    if report_raw is not None:
        try:
            report_text = report_raw.decode("utf-8")
        except UnicodeError:
            errors.append("discovery report is not UTF-8 text")

    sources = ledger.get("sources")
    source_ids = {}
    if not isinstance(sources, list) or not sources:
        errors.append("missing source snapshot inventory")
        sources = []
    for source in sources:
        if not isinstance(source, dict) or not _text(source.get("id")):
            errors.append("invalid source identity")
            continue
        sid = source["id"]
        if sid in source_ids:
            errors.append("duplicate source id: " + sid)
        source_ids[sid] = source.get("kind")
        if source.get("kind") not in SOURCE_KINDS:
            errors.append(sid + ": unknown source kind")
        if not _text(source.get("locator")):
            errors.append(sid + ": missing original source locator")
        if source.get("kind") in ("direct_competitor", "substitute", "market") and not _text(source.get("observed_at")):
            errors.append(sid + ": missing observation date")
        _read_pinned(root, source, sid, errors)
    if "client" not in source_ids.values():
        errors.append("missing original client evidence")
    if not any(kind in ("direct_competitor", "substitute", "market") for kind in source_ids.values()):
        errors.append("no externally observed market evidence")

    dimensions = ledger.get("dimensions")
    if not isinstance(dimensions, dict):
        dimensions = {}
        errors.append("missing research dimensions")
    unknown_dimensions = set(dimensions) - set(DIMENSIONS)
    if unknown_dimensions:
        errors.append("unknown dimensions: " + ", ".join(sorted(unknown_dimensions)))
    finding_ids = set()
    finding_groups = {}
    validation_texts = []
    for dimension, minimum in DIMENSIONS.items():
        entries = dimensions.get(dimension)
        if not isinstance(entries, list) or len(entries) < minimum:
            errors.append(dimension + ": insufficient structured evidence")
            continue
        for item in entries:
            if not isinstance(item, dict):
                errors.append(dimension + ": malformed finding")
                continue
            ident = item.get("id")
            if not _text(ident):
                errors.append(dimension + ": finding without id")
                continue
            if ident in finding_ids:
                errors.append("duplicate finding: " + ident)
            finding_ids.add(ident)
            finding_groups[ident] = dimension
            if not _text(item.get("claim"), 25):
                errors.append(ident + ": missing substantive claim")
            if not _text(item.get("reasoning"), 35):
                errors.append(ident + ": missing causal reasoning")
            level = item.get("evidence_level")
            if level not in EVIDENCE_LEVELS:
                errors.append(ident + ": missing fact/hypothesis classification")
            linked = item.get("source_ids")
            if not isinstance(linked, list) or not linked:
                errors.append(ident + ": no source or uncertainty evidence")
            else:
                for sid in linked:
                    if sid not in source_ids:
                        errors.append(ident + ": unknown source " + str(sid))
                if level == "client_fact" and not any(source_ids.get(sid) == "client" for sid in linked):
                    errors.append(ident + ": client fact has no client source")
            anchor = item.get("report_anchor")
            if not _text(anchor) or anchor not in report_text:
                errors.append(ident + ": finding not traceable to actual report")
            if level in ("hypothesis", "inference") and (
                not _text(item.get("open_assumption"), 15) or
                not _text(item.get("validation_action"), 18)
            ):
                errors.append(ident + ": untested inference lacks uncertainty and test")
            if level in ("hypothesis", "inference"):
                if not _text(item.get("support_signal"), 25):
                    errors.append(ident + ": hypothesis lacks claim-specific support signal")
                if not _text(item.get("falsification_signal"), 25):
                    errors.append(ident + ": hypothesis lacks claim-specific disconfirming evidence")
                if item.get("support_signal") == item.get("falsification_signal"):
                    errors.append(ident + ": support and disconfirmation are identical")
            action = item.get("validation_action")
            if _text(action):
                validation_texts.append(" ".join(action.casefold().split()))
            if dimension == "customer_journey" and not isinstance(item.get("sequence"), int):
                errors.append(ident + ": journey order missing")

    # A mechanically traceable report with a generic test repeated across
    # most unrelated claims is NOT a substantive Discovery (anti-boilerplate regression).
    # This is a coarse structural defense, not semantic truth evaluation.
    repeated = Counter(validation_texts)
    if validation_texts and repeated.most_common(1)[0][1] > max(3, int(len(validation_texts) * 0.35)):
        errors.append("generic/boilerplate validation action repeated across unrelated findings")

    # Materiality and market perspective: rentals alone are not the full choice set.
    alternatives = dimensions.get("market_alternatives", [])
    kinds = {item.get("alternative_type") for item in alternatives if isinstance(item, dict)}
    if not {"direct", "substitute"}.issubset(kinds):
        errors.append("alternatives must compare direct providers and substitutes")
    journey = dimensions.get("customer_journey", [])
    order = [x.get("sequence") for x in journey if isinstance(x, dict) and isinstance(x.get("sequence"), int)]
    if len(set(order)) != len(order):
        errors.append("journey steps are not uniquely ordered")
    for group in ("market_tensions", "strategic_opportunities", "validation_plan"):
        for item in dimensions.get(group, []):
            if not isinstance(item, dict):
                continue
            related = item.get("related_ids")
            if not isinstance(related, list) or not related:
                errors.append(str(item.get("id")) + ": no cross-links in reasoning chain")
            else:
                for rid in related:
                    if rid not in finding_ids:
                        errors.append(str(item.get("id")) + ": unknown reasoning link " + str(rid))

    audit = ledger.get("self_audit")
    if not isinstance(audit, dict):
        errors.append("missing critical second pass")
    else:
        report_sha = (ledger.get("report") or {}).get("sha256") if isinstance(ledger.get("report"), dict) else None
        if audit.get("reviewed_report_sha256") != report_sha:
            errors.append("self-audit not anchored to exact report revision")
        if audit.get("reviewer_kind") != "internal_critical_pass":
            errors.append("audit must accurately identify internal critic, not fake independence")
        checks = audit.get("checks")
        indexed = {}
        if isinstance(checks, list):
            for check in checks:
                if not isinstance(check, dict) or not _text(check.get("id")):
                    errors.append("invalid audit check")
                    continue
                if check["id"] in indexed:
                    errors.append("duplicate audit check: " + check["id"])
                indexed[check["id"]] = check
        else:
            errors.append("missing critical-review checks")
        for check_id in AUDIT_CHECKS:
            check = indexed.get(check_id)
            if not check:
                errors.append("audit missing " + check_id)
                continue
            if check.get("status") != "pass" or not _text(check.get("observation"), 35):
                errors.append("audit unresolved or superficial: " + check_id)
            inspected = check.get("finding_ids")
            if not isinstance(inspected, list) or not inspected or any(fid not in finding_ids for fid in inspected):
                errors.append("audit lacks report-linked observations: " + check_id)
        gaps = audit.get("gaps")
        if not isinstance(gaps, list):
            errors.append("self-audit missing explicit gap inventory")
        else:
            for gap in gaps:
                if not isinstance(gap, dict) or gap.get("severity") not in ("critical", "major", "minor"):
                    errors.append("invalid gap record")
                elif gap.get("severity") in ("critical", "major") and gap.get("status") != "resolved":
                    errors.append("unresolved substantive research gap: " + str(gap.get("id")))
        if not _text(audit.get("limitations"), 45):
            errors.append("missing explicit evidence/knowledge limitations")
        if audit.get("premature_art_direction") is not False:
            errors.append("art direction attempted before approved upstream gates")

    # Missing interview data or actual brand guarantees may remain OPEN and
    # explicitly labelled. Never fabricate interviews merely to satisfy RQC.
    return {
        "allowed": not errors,
        "code": "STRUCTURE_READY_FOR_EDITORIAL_REVIEW" if not errors else STOP,
        "errors": errors,
        "verified_finding_count": len(finding_ids),
        "warning": "Only source/file integrity and structured coverage checked; editorial truth and human SRA remain unverified.",
    }


def main():
    parser = argparse.ArgumentParser(description="RQC-001 first-pass Discovery evidence gate")
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
        result = validate(ledger, args.root)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"allowed": False, "code": STOP, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
