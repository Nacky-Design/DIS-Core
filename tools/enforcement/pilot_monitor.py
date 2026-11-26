"""DIS Pilot Monitor v0.1 — minimal, opt-in, GitHub-backed event trail.

Scope: route, stage changes, detected errors, attempted fixes and outcomes.
The novice's chat text, screenshots, name, email, tokens and telemetry are NOT
collected. GitHub readback proves persistence, NOT whether a model-reported
event actually occurred. Native ChatGPT actions cannot be intercepted here.

Client-specific monitor lives ONLY in the PRIVATE project repository.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
import re

SCHEMA = "DIS-PILOT-MONITOR/v1"
FILE = ".dis/pilot-monitor.json"
MAX_EVENTS = 2000
MAX_SUMMARY = 240
MAX_PILOT_ID = 64
KINDS = {
    "route_selected", "stage_entered", "stage_exit_requested",
    "stage_blocked", "error_detected", "fix_attempted", "fix_result",
    "monitor_stopped",
}
ISSUE_KINDS = {"error_detected", "fix_attempted", "fix_result"}
OUTCOMES = {"PASS_REPORTED", "FAIL_REPORTED", "NOT_CHECKED"}
ORIGINS = {"agent_reported", "operator_reported", "controller_observed"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
ISSUE_ID = re.compile(r"^ERR-[0-9]{3,6}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = re.compile(
    r"(?i)(?:bearer\s+[a-z0-9._-]{8,}|"
    r"(?:password|secret|token|api[_-]?key|пароль|токен)\s*[:=]|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|"
    r"https?://\S+)"
)


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def _digest(obj):
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _error(reason):
    return {"allowed": False, "code": "STOP_PILOT_MONITOR", "reason": reason}


def _summary_valid(value):
    return (isinstance(value, str) and 1 <= len(value.strip()) <= MAX_SUMMARY
            and not FORBIDDEN.search(value) and "\n" not in value)


def initial_log(pilot_id, *, consent=False):
    """Consent must be explicitly obtained and declared; no hidden capture."""
    if not consent:
        return _error("explicit pilot monitoring consent required")
    if not isinstance(pilot_id, str) or not SAFE_ID.fullmatch(pilot_id):
        return _error("use anonymous, non-personal pilot ID")
    return {"allowed": True, "code": "MONITOR_INITIAL_CANDIDATE",
            "log": {"schema": SCHEMA, "pilot_id": pilot_id,
                    "collection": ["route", "stage", "error", "fix"],
                    "consent_declared": True, "events": []}}


def validate_log(log):
    if not isinstance(log, dict) or log.get("schema") != SCHEMA:
        return _error("invalid monitor schema")
    if (not isinstance(log.get("pilot_id"), str) or
            not SAFE_ID.fullmatch(log["pilot_id"])):
        return _error("invalid pilot ID")
    if log.get("consent_declared") is not True:
        return _error("consent absent")
    if log.get("collection") != ["route", "stage", "error", "fix"]:
        return _error("monitor scope changed from agreed minimal scope")
    events = log.get("events")
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        return _error("invalid/excessive monitor events")
    previous = "0" * 64
    issues = {}
    halted = False
    for i, item in enumerate(events, 1):
        if not isinstance(item, dict):
            return _error("invalid event record")
        if item.get("seq") != i or item.get("previous_hash") != previous:
            return _error("broken event sequence/hash chain")
        if item.get("kind") not in KINDS or item.get("origin") not in ORIGINS:
            return _error("invalid event kind or provenance")
        if not _summary_valid(item.get("summary")):
            return _error("event contains invalid/possibly private summary")
        if not isinstance(item.get("recorded_at"), str) or not item["recorded_at"]:
            return _error("recorded_at missing")
        if not isinstance(item.get("stage"), str) or not SAFE_ID.fullmatch(item["stage"]):
            return _error("invalid/missing stage identifier")
        if halted:
            return _error("event recorded after pilot stopped")
        if item["kind"] in ISSUE_KINDS:
            issue = item.get("issue_id")
            if not isinstance(issue, str) or not ISSUE_ID.fullmatch(issue):
                return _error("missing/invalid issue ID")
            if item["kind"] == "error_detected":
                if issue in issues:
                    return _error("duplicate issue ID")
                issues[issue] = {"attempts": 0, "results": 0}
            elif issue not in issues:
                return _error("fix refers to unknown issue")
            elif item["kind"] == "fix_attempted":
                issues[issue]["attempts"] += 1
            elif item["kind"] == "fix_result":
                if issues[issue]["attempts"] <= issues[issue]["results"]:
                    return _error("fix result without prior attempt")
                if item.get("outcome") not in OUTCOMES:
                    return _error("invalid fix result")
                issues[issue]["results"] += 1
        else:
            if item.get("issue_id") is not None or item.get("outcome") is not None:
                return _error("issue/outcome fields on non-issue event")
        if item["kind"] != "fix_result" and item.get("outcome") is not None:
            return _error("outcome requires fix_result")
        expected = _digest({k: v for k, v in item.items() if k != "event_hash"})
        if item.get("event_hash") != expected:
            return _error("event payload hash mismatch")
        previous = expected
        if item["kind"] == "monitor_stopped":
            halted = True
    return {"allowed": True, "code": "MONITOR_STRUCTURE_PASS",
            "events": len(events), "issues": len(issues),
            "warning": "Hash chain detects accidental edits, not malicious Git history rewrites."}


def append_candidate(log, *, kind, stage, summary, origin="agent_reported",
                     issue_id=None, outcome=None, recorded_at=None):
    """No event is treated as independently verified just because it was saved."""
    current = validate_log(log)
    if not current["allowed"]:
        return current
    if log["events"] and log["events"][-1]["kind"] == "monitor_stopped":
        return _error("monitor stopped")
    if len(log["events"]) >= MAX_EVENTS:
        return _error("monitor capacity exceeded")
    if kind not in KINDS or origin not in ORIGINS:
        return _error("invalid kind/origin")
    if not SAFE_ID.fullmatch(stage or "") or not _summary_valid(summary):
        return _error("invalid stage/summary; avoid names, chat text, tokens and links")
    if kind in ISSUE_KINDS:
        if not ISSUE_ID.fullmatch(issue_id or ""):
            return _error("issue_id required: ERR-001")
        if kind == "fix_result" and outcome not in OUTCOMES:
            return _error("fix_result requires reported outcome")
        if kind != "fix_result" and outcome is not None:
            return _error("outcome only allowed on fix_result")
    elif issue_id is not None or outcome is not None:
        return _error("issue/outcome not applicable to this event")
    if recorded_at is None:
        recorded_at = datetime.now(timezone.utc).isoformat()
    event = {
        "seq": len(log["events"]) + 1,
        "kind": kind, "stage": stage, "summary": summary.strip(),
        "origin": origin, "recorded_at": recorded_at,
        "previous_hash": (log["events"][-1]["event_hash"] if log["events"]
                          else "0" * 64),
    }
    if issue_id is not None:
        event["issue_id"] = issue_id
    if outcome is not None:
        event["outcome"] = outcome
    event["event_hash"] = _digest(event)
    candidate = copy.deepcopy(log)
    candidate["events"].append(event)
    result = validate_log(candidate)
    if not result["allowed"]:
        return result
    return {"allowed": True, "code": "MONITOR_EVENT_CANDIDATE_NOT_SAVED",
            "candidate": candidate, "event": event}


def summarize(log):
    checked = validate_log(log)
    if not checked["allowed"]:
        return checked
    selected_route = None
    stages = []
    issues = {}
    for event in log["events"]:
        kind = event["kind"]
        if kind == "route_selected":
            selected_route = event["summary"]
        elif kind in ("stage_entered", "stage_exit_requested", "stage_blocked"):
            stages.append({"stage": event["stage"], "event": kind,
                           "summary": event["summary"]})
        elif kind == "error_detected":
            issues[event["issue_id"]] = {
                "stage": event["stage"], "problem": event["summary"],
                "attempts": [], "last_outcome": "NOT_CHECKED",
                "status": "OPEN",
            }
        elif kind == "fix_attempted":
            issues[event["issue_id"]]["attempts"].append(event["summary"])
        elif kind == "fix_result":
            problem = issues[event["issue_id"]]
            problem["last_outcome"] = event["outcome"]
            # Reported PASS is NOT an independently confirmed resolution.
            problem["status"] = ("FIX_REPORTED" if event["outcome"] == "PASS_REPORTED"
                                 else "OPEN")
    return {"allowed": True, "code": "PILOT_ROUTE_AND_ERRORS_SUMMARY",
            "pilot_id": log["pilot_id"], "selected_route": selected_route,
            "stages": stages, "issues": issues, "events": len(log["events"]),
            "warning": "Event origin and fix outcomes are self-reported unless separately corroborated."}


def _dump(log):
    return json.dumps(log, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def initialize_remote_monitor(github, repository, pilot_id, *,
                              consent=False, branch="main"):
    ready = initial_log(pilot_id, consent=consent)
    if not ready["allowed"]:
        return ready
    try:
        github.read(repository, FILE, branch)
        return _error("monitor already exists")
    except FileNotFoundError:
        pass
    except (OSError, ValueError, RuntimeError) as exc:
        return _error("cannot establish monitor absence: " + str(exc))
    try:
        created = github.create(repository, FILE, branch, _dump(ready["log"]))
        if not isinstance(created, dict) or not created.get("commit"):
            return _error("no GitHub commit returned")
        actual = github.read(repository, FILE, branch)
        if json.loads(actual["content"]) != ready["log"]:
            return _error("GitHub monitor readback mismatch")
        return {"allowed": True, "code": "MONITOR_INITIALIZED_GITHUB",
                "commit": created["commit"], "path": FILE}
    except (OSError, ValueError, RuntimeError, TypeError, KeyError) as exc:
        return _error("remote monitor initialization failed: " + str(exc))


def append_remote_event(github, repository, *, branch="main", **event):
    """Optimistic GitHub CAS + readback. No silent retry after conflict."""
    try:
        start = github.read(repository, FILE, branch)
        current = json.loads(start["content"])
        proposed = append_candidate(current, **event)
        if not proposed["allowed"]:
            return proposed
        raw = _dump(proposed["candidate"])
        result = github.write(repository, FILE, branch, raw, start["sha"])
        if not isinstance(result, dict) or not result.get("commit"):
            return _error("monitor GitHub write returned no commit")
        observed = github.read(repository, FILE, branch)
        if observed["content"] != raw:
            return _error("monitor readback differs from submitted bytes")
        return {"allowed": True, "code": "MONITOR_EVENT_SAVED",
                "commit": result["commit"], "path": FILE,
                "seq": proposed["event"]["seq"],
                "warning": "Saved model report is not independent evidence of event truth."}
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        return _error("GitHub monitor append failed/conflicted: " + str(exc))
