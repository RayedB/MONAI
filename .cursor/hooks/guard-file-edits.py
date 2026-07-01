#!/usr/bin/env python3
"""
preToolUse hook — deterministic enforcement of .cursor/rules/agent-boundaries.mdc.

Blocks file-modifying tool calls that target read-only / protected paths, turning the
"never touch" boundary from advice into a mechanism. Reads the tool call as JSON on stdin
and prints a JSON permission decision. Fail-closed: an unresolvable write target is denied.

Runs only inside Cursor (and Cursor cloud agents) — it is inert in other tools.
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys


def emit(permission, user="", agent=""):
    print(json.dumps({"permission": permission, "user_message": user, "agent_message": agent}))
    sys.exit(0)


# Repo-relative globs an agent must never modify (mirrors agent-boundaries.mdc + self-protection).
PROTECTED = [
    "monai/networks/*",
    "monai/csrc/*",
    "monai/_extensions/*",
    "monai/data/*",
    "monai/engines/*",
    "monai/apps/*",
    ".github/workflows/*",
    ".github/CODEOWNERS",
    # the guardrails themselves — an agent must not be able to disable its own boundaries
    ".cursor/hooks.json",
    ".cursor/hooks/*",
    ".cursor/rules/agent-boundaries.mdc",
    # build / release / tooling config
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "versioneer.py",
    "monai/_version.py",
    "runtests.sh",
    ".pre-commit-config.yaml",
]

# Verbs that mark a file-MODIFYING tool (substring match on tool_name, case-insensitive).
WRITE_VERBS = (
    "write",
    "edit",
    "replace",
    "create",
    "delete",
    "remove",
    "move",
    "rename",
    "patch",
    "apply",
    "modify",
    "insert",
    "mkdir",
    "touch",
)

# Likely keys holding the target path in tool_input (NOT content keys like old_string).
PATH_KEYS = ("file_path", "path", "target_file", "relative_workspace_path", "filePath", "file", "fileName", "uri")

ALLOWED_NOTE = (
    "Allowed for agents: a transform's array.py/dictionary.py, "
    "monai/transforms/__init__.py, docs/source/transforms.rst, "
    "tests/transforms/test_*. A human must change anything else."
)


def find_path(ti):
    for k in PATH_KEYS:
        v = ti.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # last resort: a single path-looking string value
    cands = [v for v in ti.values() if isinstance(v, str) and ("/" in v or "\\" in v) and "." in os.path.basename(v)]
    return cands[0] if len(cands) == 1 else None


def main():
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    tool = str(data.get("tool_name", "")).lower()
    ti = data.get("tool_input")
    ti = ti if isinstance(ti, dict) else {}

    # Not a file-modifying tool → not our concern (reads of protected files are allowed).
    if not any(v in tool for v in WRITE_VERBS):
        emit("allow")

    target = find_path(ti)
    if not target:
        emit(
            "deny",
            "🔒 Boundary hook: couldn't identify the file path for a write; denied.",
            "Could not locate the target path. tool_input keys seen: ["
            + ", ".join(sorted(ti.keys()))
            + "]. Add the real key to PATH_KEYS in "
            ".cursor/hooks/guard-file-edits.py.",
        )

    cwd = data.get("cwd") or os.getcwd()
    ap = target if os.path.isabs(target) else os.path.normpath(os.path.join(cwd, target))
    rel = os.path.relpath(ap, cwd).replace(os.sep, "/")

    for pat in PROTECTED:
        if rel == pat or fnmatch.fnmatch(rel, pat):
            emit(
                "deny",
                f"🔒 agent-boundaries: {rel} is read-only for agents.",
                f"Blocked: {rel} is outside the allowed edit set. {ALLOWED_NOTE} "
                "See .cursor/rules/agent-boundaries.mdc.",
            )

    emit("allow")


try:
    main()
except Exception as e:  # never crash silently — fail-closed
    emit("deny", "Boundary hook error; denied to stay safe.", f"guard-file-edits.py crashed: {e!r}")
