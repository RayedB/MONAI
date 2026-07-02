# /approve-tests — human approval gate for test design

The **human checkpoint** where a domain owner approves (or rejects) the tests engineering proposed
for a transform request. See `LIFECYCLE.md` at the repo root: this is the `stage:test-review` gate.

## Hard rules
- **Human-only. Never auto-approve.** You summarize and ask; the human decides. Do not infer
  approval, and do not advance without an explicit "approve."
- **No code edits.** This command only reads the issue and updates labels/comments — it never touches
  source or tests.
- **Plain language.** Describe the test *scenarios* in words; don't dump code at the reviewer.

## Steps
1. **Input:** an issue number `<n>`.
2. **Fetch:** `gh issue view <n> --comments`. Read the issue body (the original request) and find the
   **agent's latest test-design comment** (the proposed test scenarios).
   - If there's no test-design comment, or the issue isn't at `stage:test-review`, say so and stop —
     there's nothing to approve yet.
3. **Summarize for a domain owner** — focus on what they can actually judge:
   - **Does the behavior match the request?** Compare the proposed tests to the issue's "what it
     should do," and call out any mismatch.
   - **Are these the right edge cases?** Explain each in plain terms — e.g. value **overflow**
     (numbers pushed past the allowed range), **empty mask** (no labeled region present),
     **odd dimensions** (unusual image sizes) — and ask whether an important case is missing.
   - **Does cross-backend agreement matter here?** i.e. must the result be the same whether the data
     is a PyTorch tensor or a NumPy array? (Usually yes for transforms.)
   - **Deterministic vs random**, if relevant: for random transforms, are the tests checking the
     *range / reproducibility* rather than one fixed output?
4. **Ask:** "Approve, or request changes?"

## On the human's decision
**Approve** — only on an explicit yes. Record the approver (their name, or `git config user.name`),
then run the **single atomic gate action** — label swap + approval comment + cloud dispatch in one
deterministic script (never run the three steps individually; a partial execution leaves the
machine in a lying state):
```
.cursor/scripts/approve-dispatch.sh <n> "<approver>"
```
It POSTs the automation's webhook from the approver's machine (instant — no CI queue), reading
`CURSOR_AUTOMATION_WEBHOOK_*` from the approver's environment (never committed). **Show the
script's output** — it must end with the dispatch confirmation (`{"success":true,...}`). If it
fails on missing env, fall back to the CI relay: `gh workflow run scaffold-agent.yml -f issue=<n>`
(same webhook, via Actions — may queue).

Then say plainly: the tests are approved and **the approval itself dispatched the builder** — the
cloud agent builds from the approved test design and opens a PR. The resulting code goes through
its **own** human review before merge.

**Request changes:**
```
gh issue comment <n> --body "Changes requested on test design (<reviewer>):
<the reviewer's notes>"
gh issue edit <n> --remove-label "stage:test-review" --add-label "stage:test-design"
```
Then say plainly: the notes are recorded and it's back with engineering to revise the tests.

> Requires `gh` with **push access** (the `RayedB` account in this environment;
> `gh auth switch --user RayedB` if a write returns `HTTP 404`).

## Boundary
You move work *out of* a review gate **only because a human explicitly told you to**. You never
approve, never auto-advance, and never edit code from this command.
