#!/usr/bin/env python3
"""
beforeShellExecution hook — enforces "agents only move work INTO review; humans own every
gate" (see LIFECYCLE.md) and blocks destructive / governance commands. Reads the command as
JSON on stdin and prints a JSON permission decision. Fail-closed.

Allowed: opening PRs, pushing feature branches, moving issue labels INTO review.
Denied: crossing a gate (merge, push to dev/main) or destructive/governance ops (delete, force-push).

Runs only inside Cursor (and Cursor cloud agents) — it is inert in other tools.
"""
import sys, json, re, shlex


def emit(permission, user="", agent=""):
    print(json.dumps({"permission": permission, "user_message": user, "agent_message": agent}))
    sys.exit(0)


PROTECTED_BRANCHES = ("dev", "main", "master")


def deny_reason(cmd):
    try:
        toks = shlex.split(cmd)
    except Exception:
        toks = cmd.split()
    ts = set(toks)

    if re.search(r"\bgh\b.*\bpr\b.*\bmerge\b", cmd):
        return "Merging is a human gate — agents only move work INTO review, never past it."
    if re.search(r"\bgh\b.*\b(issue|label|repo)\b.*\bdelete\b", cmd):
        return "Deleting issues/labels/repos is not an agent action."

    if "git" in ts and "push" in ts:
        if {"--force", "-f", "--force-with-lease"} & ts or re.search(r"push\s+\S+\s+\+\S", cmd):
            return "Force-push rewrites history — blocked for agents."
        if "--delete" in ts:
            return "Deleting remote branches is not an agent action."
        for b in PROTECTED_BRANCHES:
            if b in ts or f"HEAD:{b}" in ts or any(t.endswith(":" + b) for t in toks):
                return f"Direct push to '{b}' bypasses the PR review gate — open a PR instead."

    if "git" in ts and "reset" in ts and "--hard" in ts:
        return "git reset --hard can destroy work — do this manually."
    if "git" in ts and "branch" in ts and "-D" in ts:
        return "Force-deleting branches is not an agent action."
    return None


def main():
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    cmd = str(data.get("command", ""))
    reason = deny_reason(cmd)
    if reason:
        emit("deny", f"🔒 {reason}",
             f"Blocked by shell guard: {reason} A human must run this. (command: {cmd!r})")
    emit("allow")


try:
    main()
except Exception as e:  # never crash silently — fail-closed
    emit("deny", "Shell guard error; denied to stay safe.", f"guard-shell.py crashed: {e!r}")
