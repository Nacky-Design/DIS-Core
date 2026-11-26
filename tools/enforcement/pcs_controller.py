#!/usr/bin/env python3
"""DIS PCS-001 pilot: fail-closed stage packet compiler and signed approval verifier.

This is a CLI/library for a controlled local checkout, NOT an interceptor for
ChatGPT image generation, Figma or browser-hosted Codex. Signing key must be
held by a separate trusted approval issuer, never exposed to the creative agent.
"""
import argparse
import hashlib
import hmac
import json
from pathlib import Path

SCHEMA = "PCS-001/v1"
REQUIRED_KINDS = {"client_baseline", "discovery", "semantic_architecture", "prototype", "art_direction", "frankenstein", "ui_kit"}
ALLOWED_STATES = {"approved_by_user", "proposed", "reviewed", "source_verified"}
STOP = "STOP_PCS_PREFLIGHT"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_file(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("absolute/empty file path")
    base = Path(root).resolve()
    target = (base / relative).resolve()
    if not target.is_relative_to(base) or not target.is_file():
        raise ValueError("inaccessible or unsafe path: " + relative)
    return target


def compile_packet(manifest, root):
    errors = []
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        return {"allowed": False, "code": STOP, "errors": ["invalid PCS schema"]}
    for field in ("project", "stage_id", "scope", "prompt", "sources", "decisions"):
        if not manifest.get(field):
            errors.append("missing " + field)
    sources = manifest.get("sources", [])
    decisions = manifest.get("decisions", [])
    if not isinstance(sources, list) or not isinstance(decisions, list):
        return {"allowed": False, "code": STOP, "errors": errors + ["sources/decisions must be arrays"]}
    loaded = []
    kinds = set()
    for s in sources:
        if not isinstance(s, dict):
            errors.append("invalid source record")
            continue
        source_id = s.get("id", "?")
        kind = s.get("kind")
        state = s.get("status")
        if kind in kinds and kind != "reference":
            errors.append("duplicate source kind: " + str(kind))
        kinds.add(kind)
        if state not in ALLOWED_STATES:
            errors.append(str(source_id) + ": invalid source status")
        if state == "approved_by_user" and not s.get("approval_ref"):
            errors.append(str(source_id) + ": missing approval reference")
        if kind == "ui_kit" and state == "approved_by_user" and not s.get("approval_ref"):
            errors.append("UI Kit must not be silently promoted")
        if kind not in ("ui_kit", "client_baseline", "reference", "competitive_research", "semantic_architecture") and state != "approved_by_user":
            errors.append(str(source_id) + ": predecessor not approved")
        if kind == "competitive_research" and state not in ("approved_by_user", "reviewed"):
            errors.append(str(source_id) + ": competitor audit not accepted/reviewed")
        if kind == "semantic_architecture" and state != "approved_by_user":
            scope_ref = s.get("approved_core_ref")
            if state != "reviewed" or not scope_ref:
                errors.append(str(source_id) + ": semantic source not approved and no approved-core exception")
            elif not any(isinstance(other, dict) and other.get("kind") == "prototype" and
                         other.get("status") == "approved_by_user" and
                         other.get("approval_ref") == scope_ref for other in sources):
                errors.append(str(source_id) + ": semantic approved core is not confirmed by approved prototype")
        if kind == "ui_kit" and state == "proposed":
            pass  # Candidate UI Kit must never become approved via import.
        try:
            file = safe_file(root, s.get("path"))
            data = file.read_bytes()
            actual = digest(data)
            if not s.get("sha256") or not hmac.compare_digest(actual, s["sha256"]):
                errors.append(str(source_id) + ": source digest mismatch")
            if kind == "client_baseline":
                if not s.get("original_binary_path") or not s.get("original_binary_sha256"):
                    errors.append(str(source_id) + ": original client brief path/hash missing")
                else:
                    original_file = safe_file(root, s["original_binary_path"])
                    original_hash = digest(original_file.read_bytes())
                    if not hmac.compare_digest(original_hash, s["original_binary_sha256"]):
                        errors.append(str(source_id) + ": original client brief digest mismatch")
            if s.get("text_path"):
                textfile = safe_file(root, s["text_path"])
                text_bytes = textfile.read_bytes()
                text_digest = digest(text_bytes)
                if not s.get("text_sha256") or not hmac.compare_digest(text_digest, s["text_sha256"]):
                    errors.append(str(source_id) + ": source extracted-text digest mismatch")
                readable_text = text_bytes.decode("utf-8")
            else:
                text_digest = None
                readable_text = data.decode("utf-8")
            loaded.append({"id": source_id, "kind": kind, "path": s["path"], "url": s.get("url"), "status": state,
                           "sha256": actual, "approval_ref": s.get("approval_ref"),
                           "approved_core_ref": s.get("approved_core_ref"),
                           "text_path": s.get("text_path"), "text_sha256": text_digest,
                           "original_binary_path": s.get("original_binary_path"),
                           "original_binary_sha256": s.get("original_binary_sha256"),
                           "full_text": readable_text})
        except (OSError, ValueError, UnicodeError, TypeError) as exc:
            errors.append(str(source_id) + ": " + str(exc))
    missing = REQUIRED_KINDS - kinds
    if missing:
        errors.append("missing mandatory source kinds: " + ", ".join(sorted(missing)))
    active = []
    seen = set()
    for d in decisions:
        if not isinstance(d, dict) or not d.get("id"):
            errors.append("decision missing id")
            continue
        ident = d["id"]
        if ident in seen:
            errors.append("duplicate decision id: " + ident)
        seen.add(ident)
        if d.get("status") != "approved_by_user":
            errors.append(ident + ": unapproved active decision")
        if d.get("lock") not in ("LOCKED", "GUIDED", "OPEN"):
            errors.append(ident + ": missing LOCKED/GUIDED/OPEN")
        if not d.get("source_id") or d["source_id"] not in {s.get("id") for s in sources if isinstance(s, dict)}:
            errors.append(ident + ": source not listed")
        if not d.get("scope") or not d.get("approval_ref"):
            errors.append(ident + ": approval or scope missing")
        if d.get("conflict") and not d.get("resolved_by"):
            errors.append(ident + ": unresolved conflict")
        active.append(d)
    prompt = manifest.get("prompt", {})
    prompt_data = ""
    if not isinstance(prompt, dict) or not prompt.get("id") or not prompt.get("version"):
        errors.append("missing prompt id/version")
    else:
        try:
            p = safe_file(root, prompt.get("path"))
            data = p.read_bytes()
            if not prompt.get("sha256") or not hmac.compare_digest(digest(data), prompt["sha256"]):
                errors.append("prompt digest mismatch")
            prompt_data = data.decode("utf-8")
        except (OSError, ValueError, UnicodeError, TypeError) as exc:
            errors.append("prompt: " + str(exc))
    if manifest.get("stage_id") == "FA-01-HERO":
        if manifest.get("scope") != "HERO":
            errors.append("HERO stage scope mismatch")
        for ref in ("Fin", "Legora", "Micro", "Weavy", "Q Industrial"):
            if not any(d.get("id") == "hero.ref." + ref and d.get("status") == "approved_by_user" for d in active):
                errors.append("missing HERO reference decision: " + ref)
        for ident in ("hero.semantic.A+C", "hero.no_fake_metrics", "hero.no_kicker",
                      "hero.no_saas_cards", "hero.typography_spatial", "hero.no_diagrams"):
            if not any(d.get("id") == ident and d.get("status") == "approved_by_user" for d in active):
                errors.append("missing HERO continuity decision: " + ident)
    if errors:
        return {"allowed": False, "code": STOP, "errors": errors,
                "loaded_sources": [{"id": s["id"], "path": s["path"], "sha256": s["sha256"]} for s in loaded]}
    snapshot = {"schema": SCHEMA, "project": manifest["project"], "stage_id": manifest["stage_id"],
                "scope": manifest["scope"], "dec_contract_path": manifest.get("dec_contract_path"), "prompt": {**prompt, "full_text": prompt_data},
                "sources": loaded, "decisions": active, "author_additions": manifest.get("author_additions", "")}
    return {"allowed": True, "code": "READY_FOR_STAGE_START_APPROVAL",
            "snapshot_sha256": digest(canonical(snapshot)), "snapshot": snapshot}


def verify_approval(snapshot_sha256, receipt, kind, stage_id, scope, signing_key):
    """Receipt is issued by a SEPARATE privileged human-approval service."""
    if not signing_key:
        return {"allowed": False, "code": "STOP_TRUSTED_ISSUER_NOT_CONNECTED"}
    if not isinstance(receipt, dict):
        return {"allowed": False, "code": "STOP_APPROVAL_MISSING"}
    fields = ("kind", "snapshot_sha256", "stage_id", "scope", "decision", "actor", "nonce")
    if any(not receipt.get(k) for k in fields):
        return {"allowed": False, "code": "STOP_APPROVAL_INCOMPLETE"}
    if (receipt["kind"], receipt["snapshot_sha256"], receipt["stage_id"], receipt["scope"], receipt["decision"]) != (
        kind, snapshot_sha256, stage_id, scope, "approved"):
        return {"allowed": False, "code": "STOP_APPROVAL_SCOPE_OR_VERSION"}
    payload = {k: receipt[k] for k in fields}
    expected = hmac.new(signing_key, canonical(payload), hashlib.sha256).hexdigest()
    if not isinstance(receipt.get("signature"), str) or not hmac.compare_digest(expected, receipt["signature"]):
        return {"allowed": False, "code": "STOP_APPROVAL_SIGNATURE"}
    return {"allowed": True, "code": "APPROVAL_VALID", "actor": receipt["actor"]}



def verify_snapshot_freshness(start_packet, root):
    """Recheck every pinned input immediately before promoting an output."""
    snapshot = start_packet.get("snapshot", {}) if isinstance(start_packet, dict) else {}
    errors = []
    records = list(snapshot.get("sources", [])) + [snapshot.get("prompt", {})]
    for row in records:
        try:
            actual = digest(safe_file(root, row.get("path")).read_bytes())
            if actual != row.get("sha256"):
                errors.append("stale input: " + str(row.get("path")))
            if row.get("original_binary_path"):
                original_actual = digest(safe_file(root, row["original_binary_path"]).read_bytes())
                if original_actual != row.get("original_binary_sha256"):
                    errors.append("stale original binary: " + str(row["original_binary_path"]))
            if row.get("text_path"):
                text_actual = digest(safe_file(root, row["text_path"]).read_bytes())
                if text_actual != row.get("text_sha256"):
                    errors.append("stale extracted text: " + str(row["text_path"]))
        except (OSError, ValueError, TypeError) as exc:
            errors.append("unreadable input: " + str(exc))
    return errors


def compile_result_packet(start_packet, start_receipt, signing_key, artifact_path, qa_path, root):
    """Bind an actual artifact and documented QA to an immutable result snapshot.

    This does NOT grant artistic approval; its digest must receive a separate
    trusted stage_result human signature. QA assertions remain evidence to
    inspect, not automatically trusted.
    """
    errors = []
    if not isinstance(start_packet, dict) or not start_packet.get("allowed") or not start_packet.get("snapshot_sha256") or not isinstance(start_packet.get("snapshot"), dict):
        return {"allowed": False, "code": "STOP_UNAPPROVED_STAGE_INPUT", "errors": ["start packet invalid"]}
    check = verify_approval(start_packet["snapshot_sha256"], start_receipt, "stage_start",
                            start_packet["snapshot"]["stage_id"], start_packet["snapshot"]["scope"], signing_key)
    if not check["allowed"]:
        return {"allowed": False, "code": "STOP_START_APPROVAL_NOT_VERIFIED", "errors": [check["code"]]}
    # DEC-001 is an additional fail-closed gate for projects whose manifest
    # declares a stage-scoped execution ledger. This does NOT intercept direct
    # image/Figma calls; it governs only this controlled PCS result route.
    dec_path = start_packet["snapshot"].get("dec_contract_path")
    if dec_path:
        try:
            from dec_controller import validate_pre_execution, audit_actual_artifact
            ledger = json.loads(safe_file(root, dec_path).read_text(encoding="utf-8"))
            source_rows = []
            for row in start_packet["snapshot"]["sources"]:
                source_rows.append({
                    "id": row["id"], "path": row["path"],
                    "sha256": row["sha256"], "status": row["status"],
                })
            pcs_view = {
                "project": start_packet["snapshot"]["project"],
                "stage_id": start_packet["snapshot"]["stage_id"],
                "scope": start_packet["snapshot"]["scope"],
                "prompt": start_packet["snapshot"]["prompt"],
                "sources": source_rows,
                "decisions": start_packet["snapshot"]["decisions"],
            }
            check_dec = validate_pre_execution(ledger, pcs_view, root)
            if not check_dec["allowed"]:
                return {"allowed": False, "code": "STOP_DEC_001",
                        "errors": check_dec["errors"]}
            # Full artifact QA must contain mapped DEC requirement checks;
            # generic PCS QA checks alone cannot claim compliance.
            qa_report = json.loads(safe_file(root, qa_path).read_text(encoding="utf-8"))
            checked = audit_actual_artifact(ledger, pcs_view, root, artifact_path, qa_report)
            if not checked["allowed"]:
                return {"allowed": False, "code": "STOP_DEC_ARTIFACT_QA",
                        "errors": checked["errors"]}
        except (OSError, ValueError, TypeError, ImportError) as exc:
            return {"allowed": False, "code": "STOP_DEC_001",
                    "errors": [str(exc)]}
    changed = verify_snapshot_freshness(start_packet, root)
    if changed:
        return {"allowed": False, "code": "STOP_STALE_STAGE_INPUT", "errors": changed}
    try:
        artifact = safe_file(root, artifact_path)
        qa_file = safe_file(root, qa_path)
        artifact_bytes = artifact.read_bytes()
        qa_bytes = qa_file.read_bytes()
        report = json.loads(qa_bytes.decode("utf-8"))
        if not isinstance(report, dict) or not report.get("reviewer") or not report.get("checks"):
            errors.append("QA evidence incomplete")
        else:
            checks = report["checks"]
            if not isinstance(checks, list) or not checks:
                errors.append("QA checks absent")
            if any(not isinstance(c, dict) or c.get("status") != "PASS" or not c.get("evidence") for c in checks):
                errors.append("QA has failed/unverified checks")
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        errors.append(str(exc))
    if errors:
        return {"allowed": False, "code": "STOP_RESULT_QA", "errors": errors}
    result = {"schema": SCHEMA, "stage_id": start_packet["snapshot"]["stage_id"],
              "scope": start_packet["snapshot"]["scope"],
              "start_snapshot_sha256": start_packet["snapshot_sha256"],
              "artifact_path": artifact_path, "artifact_sha256": digest(artifact_bytes),
              "qa_path": qa_path, "qa_sha256": digest(qa_bytes)}
    return {"allowed": True, "code": "READY_FOR_SEPARATE_STAGE_RESULT_APPROVAL",
            "result_sha256": digest(canonical(result)), "result": result,
            "warning": "QA evidence is not independent human approval."}


def main():
    ap = argparse.ArgumentParser(description="DIS PCS-001 packet compiler; fail-closed")
    ap.add_argument("--root", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output")
    args = ap.parse_args()
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        result = compile_packet(manifest, args.root)
    except (OSError, ValueError) as exc:
        result = {"allowed": False, "code": STOP, "errors": [str(exc)]}
    if args.output and result["allowed"]:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "snapshot"}, ensure_ascii=False))
    return 0 if result["allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
