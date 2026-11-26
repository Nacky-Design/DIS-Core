"""Validate a self-contained public DIS Core package.

Must not be run against private repo as-is: only against the export tree.
All local Markdown targets (including anchors to files) must resolve.
"""
from pathlib import Path
import re

MD_LINKS = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_ROOTS = ("projects/", "pilots/", "decisions/", "audits/", ".git/")


def verify_local_links(files):
    """Map path -> bytes or UTF-8 strings. Works before packaging."""
    names = set(files)
    errors = []
    checked = 0
    for name, content in files.items():
        if not name.endswith(".md"):
            continue
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        for match in MD_LINKS.finditer(text):
            href = match.group(1).strip().strip("<>").split()[0]
            if not href or href.startswith(("#", "https://", "http://", "mailto:")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            # A public distribution may link to local files, never to a
            # private pilot or a path outside the release root.
            path = Path(name).parent / target
            stack = []
            for part in path.parts:
                if part in ("", "."):
                    continue
                if part == "..":
                    if stack:
                        stack.pop()
                    else:
                        errors.append(f"{name}: path escapes archive: {href}")
                        stack = []
                        break
                else:
                    stack.append(part)
            dest = "/".join(stack)
            checked += 1
            if dest.startswith(FORBIDDEN_ROOTS):
                errors.append(f"{name}: linked confidential destination: {href}")
            elif dest not in names:
                errors.append(f"{name}: unresolved local link: {href}")
    return {"allowed": not errors, "code": "LINK_CLOSURE_PASS" if not errors else "STOP_BROKEN_PUBLIC_LINKS",
            "checked_links": checked, "errors": errors}
