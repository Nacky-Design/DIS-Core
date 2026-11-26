"""Optional GitHub Contents API transport for DIS project state.

This is a backend/server-side adapter, NOT something ChatGPT's read-only
GitHub integration or an unprivileged agent automatically possesses.
Credentials must be provided through a trusted environment and NEVER kept
in a project repo or copied into the prompt. A token with approved Content
read/write permission for exactly the client repo is required for writes.
"""
from __future__ import annotations

import base64
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")
PATH = ".dis/project-state.json"


class GitHubContentsClient:
    def __init__(self, token=None, timeout=15):
        self._token = token if token is not None else os.getenv("DIS_GITHUB_TOKEN")
        self.timeout = timeout
        if not self._token:
            raise ValueError("DIS_GITHUB_TOKEN / repo-scoped GitHub credential required")

    def _request(self, method, repository, path, *, branch, payload=None):
        if not isinstance(repository, str) or not REPO_PATTERN.fullmatch(repository):
            raise ValueError("invalid repository owner/name")
        if path != PATH:
            raise ValueError("only the DIS project state file is writable through this adapter")
        if not branch or not isinstance(branch, str) or ".." in branch:
            raise ValueError("invalid branch")
        repo_url = "/".join(quote(part, safe="") for part in repository.split("/"))
        url = ("https://api.github.com/repos/" + repo_url +
               "/contents/" + quote(path, safe="/"))
        if method == "GET":
            url += "?ref=" + quote(branch, safe="")
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self._token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DIS-ControlledProjectState/2",
        }
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            # Only HTTP 404 while READING is a valid "new project" signal.
            if method == "GET" and exc.code == 404:
                raise FileNotFoundError("GitHub project state not found") from None
            # Do not disclose the private API error body or any credentials.
            raise RuntimeError("GitHub Contents HTTP status " + str(exc.code)) from None
        except URLError as exc:
            raise RuntimeError("GitHub Contents connection failed") from exc

    def read(self, repository, path, branch):
        data = self._request("GET", repository, path, branch=branch)
        if (not isinstance(data, dict) or data.get("type") != "file" or
                data.get("encoding") != "base64"):
            raise RuntimeError("unexpected GitHub file response")
        try:
            raw = base64.b64decode(data["content"], validate=False)
            text = raw.decode("utf-8")
        except (KeyError, ValueError, UnicodeError) as exc:
            raise RuntimeError("invalid GitHub project state bytes") from exc
        return {"content": text, "sha": data["sha"],
                "commit": None}

    def write(self, repository, path, branch, content, expected_blob_sha):
        if not isinstance(content, str) or not expected_blob_sha:
            raise ValueError("UTF-8 content and expected blob SHA required")
        payload = {
            "message": "dis(state): update verified project checkpoint",
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "sha": expected_blob_sha,
            "branch": branch,
        }
        data = self._request("PUT", repository, path, branch=branch, payload=payload)
        result = data.get("commit") if isinstance(data, dict) else None
        if not isinstance(result, dict) or not isinstance(result.get("sha"), str):
            raise RuntimeError("GitHub write returned no commit SHA")
        return {"commit": result["sha"]}

    def create(self, repository, path, branch, content):
        """Create only the initial project state. Never overwrite an existing file."""
        if not isinstance(content, str):
            raise ValueError("UTF-8 content required")
        payload = {
            "message": "dis(state): initialize project",
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": branch,
        }
        data = self._request("PUT", repository, path, branch=branch, payload=payload)
        result = data.get("commit") if isinstance(data, dict) else None
        if not isinstance(result, dict) or not isinstance(result.get("sha"), str):
            raise RuntimeError("GitHub initial write returned no commit SHA")
        return {"commit": result["sha"]}
