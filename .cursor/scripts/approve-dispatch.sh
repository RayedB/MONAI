#!/usr/bin/env bash
# The approve-gate action (stage:test-review -> stage:scaffold), atomically:
# label swap + approval comment + cloud-automation dispatch in ONE command, so
# an agent running /approve-tests cannot half-execute the procedure (see
# LIFECYCLE.md). Run by a HUMAN's machine after an explicit "approve".
#
# Usage: .cursor/scripts/approve-dispatch.sh <issue-number> <approver-name>
#
# Requires CURSOR_AUTOMATION_WEBHOOK_URL + CURSOR_AUTOMATION_WEBHOOK_TOKEN in
# the environment (approver's shell profile — never committed). Non-interactive
# shells may skip ~/.zshrc, so we fall back to reading the exports from it.
set -euo pipefail

n="${1:?usage: approve-dispatch.sh <issue-number> <approver-name>}"
approver="${2:?usage: approve-dispatch.sh <issue-number> <approver-name>}"

if [ -z "${CURSOR_AUTOMATION_WEBHOOK_URL:-}" ] || [ -z "${CURSOR_AUTOMATION_WEBHOOK_TOKEN:-}" ]; then
  [ -f "$HOME/.zshrc" ] && eval "$(grep '^export CURSOR_AUTOMATION' "$HOME/.zshrc" || true)"
fi
: "${CURSOR_AUTOMATION_WEBHOOK_URL:?not set — export it in your shell profile}"
: "${CURSOR_AUTOMATION_WEBHOOK_TOKEN:?not set — export it in your shell profile}"

repo="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

gh issue edit "$n" --remove-label "stage:test-review" --add-label "stage:scaffold"
gh issue comment "$n" --body "✅ Test design approved by ${approver} ($(date +%F)). Advancing to scaffold — cloud build dispatched."

resp="$(curl -sS --fail-with-body -X POST "$CURSOR_AUTOMATION_WEBHOOK_URL" \
  -H "Authorization: Bearer $CURSOR_AUTOMATION_WEBHOOK_TOKEN" \
  -H 'Content-Type: application/json' \
  --data "{\"event\":\"stage:scaffold\",\"issue_number\":\"$n\",\"repository\":\"$repo\",\"issue_url\":\"https://github.com/$repo/issues/$n\"}")"

echo "cloud scaffold automation dispatched for issue #$n: $resp"
