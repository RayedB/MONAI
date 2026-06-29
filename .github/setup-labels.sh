#!/usr/bin/env bash
# Create/update the transform-contribution lifecycle labels (see ../LIFECYCLE.md).
#
# Usage:
#   ./.github/setup-labels.sh                 # targets the repo of the current dir
#   ./.github/setup-labels.sh -R owner/repo   # targets a specific repo
#
# Idempotent: --force updates a label if it already exists. Requires an authenticated `gh`.
set -euo pipefail

REPO_ARGS=("$@")  # pass-through, e.g. -R owner/repo

label() {
  # ${arr[@]+"${arr[@]}"} expands to nothing when empty — safe under `set -u` on bash 3.2 (macOS).
  gh label create "$1" --color "$2" --description "$3" --force ${REPO_ARGS[@]+"${REPO_ARGS[@]}"}
}

# Persistent type classifier
label "type:transform-request" "5319e7" "New transform requested — persistent type marker (owner: requester/PM)"

# Stages (current position in the machine)
label "stage:triage"       "d4c5f9" "Intake — checking the request is clear enough before test design (owner: triager)"
label "stage:test-design"  "1d76db" "Drafting tests for the requested transform (owner: test-design agent)"
label "stage:test-review"  "fbca04" "GATE: human reviews the test design (owner: QA/maintainer)"
label "stage:scaffold"     "0052cc" "Generating the array+dictionary pair and tests (owner: engineer + scaffold agent)"
label "stage:in-review"    "d93f0b" "GATE: PR open, human review + Bugbot/Security (owner: maintainer)"
label "stage:done"         "0e8a16" "Merged and closed (owner: maintainer)"

# Priority (orthogonal, set at triage)
label "priority:low"     "c2e0c6" "Low priority"
label "priority:medium"  "fef2c0" "Medium priority"
label "priority:high"    "e11d21" "High priority"

echo "Done. Created/updated 10 lifecycle labels."
