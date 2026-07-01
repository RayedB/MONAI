#!/usr/bin/env python3
"""
Deterministic template check for transform-request issues (stage:triage intake).

Reads the issue body on stdin and verifies the required sections exist and are
non-empty. Runs BEFORE the triage agent in CI — an issue that fails here is
rejected (comment + `invalid` label + closed as not planned) without spending an
agent run. See LIFECYCLE.md → "Automation".

Accepts BOTH legitimate formats:
  - the issue form (.github/ISSUE_TEMPLATE/transform-request.yml) → "### What should it do?"
  - the /request-transform command draft                          → "## What it should do"

Output: writes `ok=true|false` and `missing=<comma list>` to $GITHUB_OUTPUT when
set (CI), and always prints a JSON verdict to stdout (local use / logs).
"""

from __future__ import annotations

import json
import os
import re
import sys

# Required sections: canonical name -> regex matched against normalized headings.
# Normalization: lowercase, punctuation stripped. "Deterministic or random" is NOT
# required — the issue form doesn't ask it (the triage agent probes it instead).
REQUIRED = {
    "what it should do": re.compile(r"what (should it|it should) do"),
    "why it is needed": re.compile(r"^why\b"),
    "category": re.compile(r"(kind of transform|suspected category|^category$)"),
    "priority": re.compile(r"(urgent|^priority$)"),
}

EMPTY_MARKERS = {"", "_no response_", "n/a", "none", "tbd", "?"}
MIN_WHAT_LEN = 15  # "what" must describe an operation, not a shrug


def sections(body: str) -> dict[str, str]:
    """Split a markdown body into {normalized heading: content}."""
    out: dict[str, str] = {}
    current = None
    for line in body.splitlines():
        m = re.match(r"^#{2,3}\s+(.+?)\s*$", line)
        if m:
            current = re.sub(r"[^a-z0-9 ]", "", m.group(1).lower()).strip()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


def check(body: str) -> tuple[bool, list[str]]:
    found = sections(body)
    missing: list[str] = []
    for name, pattern in REQUIRED.items():
        content = next((text for heading, text in found.items() if pattern.search(heading)), None)
        if content is None:
            missing.append(name)
            continue
        cleaned = content.strip().lower()
        if cleaned in EMPTY_MARKERS:
            missing.append(name)
        elif name == "what it should do" and len(cleaned) < MIN_WHAT_LEN:
            missing.append(name + " (too short to be testable)")
    return (not missing, missing)


def main() -> None:
    body = sys.stdin.read()
    ok, missing = check(body)
    verdict = {"ok": ok, "missing": missing}
    print(json.dumps(verdict))
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"ok={'true' if ok else 'false'}\n")
            f.write(f"missing={', '.join(missing)}\n")


if __name__ == "__main__":
    main()
