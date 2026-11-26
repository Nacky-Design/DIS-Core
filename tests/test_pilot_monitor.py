"""Privacy, error-lifecycle and fake-GitHub regression tests for pilot monitor."""
import copy
import hashlib
import json
import unittest

from tools.enforcement.pilot_monitor import (
    FILE, initial_log, append_candidate, validate_log, summarize,
    initialize_remote_monitor, append_remote_event,
)


class FakeRemote:
    def __init__(self):
        self.content = None
        self.revision = 0
        self.fail_write = False

    def read(self, repository, path, branch):
        if path != FILE:
            raise ValueError("wrong file")
        if self.content is None:
            raise FileNotFoundError(path)
        return {
            "content": self.content,
            "sha": hashlib.sha1(self.content.encode("utf-8")).hexdigest(),
        }

    def create(self, repository, path, branch, content):
        if self.content is not None:
            raise RuntimeError("already exists")
        self.content = content
        self.revision += 1
        return {"commit": f"fake-commit-{self.revision}"}

    def write(self, repository, path, branch, content, expected_blob_sha):
        if self.fail_write:
            raise RuntimeError("GitHub rejected update")
        if hashlib.sha1(self.content.encode("utf-8")).hexdigest() != expected_blob_sha:
            raise RuntimeError("GitHub 409 conflict")
        self.content = content
        self.revision += 1
        return {"commit": f"fake-commit-{self.revision}"}


class PilotMonitorTests(unittest.TestCase):
    def setUp(self):
        self.log = initial_log("pilot-001", consent=True)["log"]

    def add(self, kind, stage="discovery", summary="Test observation",
            **kwargs):
        result = append_candidate(
            self.log, kind=kind, stage=stage,
            summary=summary, recorded_at="2026-11-26T12:00:00+00:00",
            **kwargs,
        )
        self.assertTrue(result["allowed"], result)
        self.log = result["candidate"]
        return result

    def test_refuses_missing_consent(self):
        self.assertFalse(initial_log("pilot-001")["allowed"])

    def test_records_route_errors_attempts_and_reported_outcomes(self):
        self.add("route_selected", stage="intake", summary="Guided; hero-only")
        self.add("stage_entered", stage="discovery", summary="Started research")
        self.add("error_detected", summary="Required citation missing",
                 issue_id="ERR-001")
        self.add("fix_attempted", summary="Reopened a primary source",
                 issue_id="ERR-001")
        self.add("fix_result", summary="Source cited on revision",
                 issue_id="ERR-001", outcome="PASS_REPORTED")
        result = summarize(self.log)
        self.assertEqual(result["selected_route"], "Guided; hero-only")
        self.assertEqual(result["issues"]["ERR-001"]["status"], "FIX_REPORTED")
        self.assertEqual(len(result["issues"]["ERR-001"]["attempts"]), 1)
        self.assertEqual(result["events"], 5)

    def test_result_without_attempt_is_blocked(self):
        self.add("error_detected", issue_id="ERR-001")
        out = append_candidate(
            self.log, kind="fix_result", stage="discovery",
            summary="It is fixed", issue_id="ERR-001", outcome="PASS_REPORTED",
        )
        self.assertFalse(out["allowed"])

    def test_fix_for_nonexistent_issue_blocked(self):
        self.assertFalse(append_candidate(
            self.log, kind="fix_attempted", stage="discovery",
            summary="Patch", issue_id="ERR-700",
        )["allowed"])

    def test_summaries_do_not_capture_personal_email_urls_or_tokens(self):
        for s in ("hello@private.example", "https://private.example",
                  "API_KEY: something", "Bearer secret123456789"):
            self.assertFalse(append_candidate(
                self.log, kind="error_detected", stage="intake",
                summary=s, issue_id="ERR-001",
            )["allowed"], s)

    def test_tampered_history_is_rejected(self):
        self.add("error_detected", issue_id="ERR-001")
        log = copy.deepcopy(self.log)
        log["events"][0]["summary"] = "different content"
        self.assertFalse(validate_log(log)["allowed"])

    def test_stop_disallows_subsequent_events(self):
        self.add("monitor_stopped", stage="intake",
                 summary="Pilot monitoring disabled")
        self.assertFalse(append_candidate(
            self.log, kind="stage_entered",
            stage="discovery", summary="New stage",
        )["allowed"])

    def test_remote_initialization_requires_consent_and_readback(self):
        api = FakeRemote()
        self.assertFalse(initialize_remote_monitor(
            api, "private/test-repo", "pilot-001"
        )["allowed"])
        start = initialize_remote_monitor(
            api, "private/test-repo", "pilot-001", consent=True
        )
        self.assertEqual(start["code"], "MONITOR_INITIALIZED_GITHUB")
        self.assertEqual(api.revision, 1)
        self.assertFalse(initialize_remote_monitor(
            api, "private/test-repo", "pilot-001", consent=True
        )["allowed"])

    def test_remote_append_requires_successful_write_and_readback(self):
        api = FakeRemote()
        initialize_remote_monitor(api, "private/test-repo", "pilot-001", consent=True)
        result = append_remote_event(
            api, "private/test-repo", kind="stage_entered", stage="intake",
            summary="Intake started", origin="agent_reported",
        )
        self.assertEqual(result["code"], "MONITOR_EVENT_SAVED")
        self.assertEqual(api.revision, 2)
        api.fail_write = True
        failed = append_remote_event(
            api, "private/test-repo", kind="stage_entered", stage="discovery",
            summary="Discovery started",
        )
        self.assertFalse(failed["allowed"])
        self.assertEqual(api.revision, 2)


if __name__ == "__main__":
    unittest.main()
