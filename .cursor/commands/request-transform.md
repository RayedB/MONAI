# /request-transform — file a transform request (plain-language intake)

Help a **non-engineer** (a researcher or imaging engineer) turn an idea into a well-formed transform
request issue. You capture **intent only** — engineering designs and builds it later, behind a human
review gate (see `LIFECYCLE.md` at the repo root).

## Hard rules
- **Plain language only.** The person you're talking to is not a software engineer. Never show source
  code, class names, or math. Don't ask them to run anything — you run the commands yourself.
- **One question at a time.** Ask, wait for the answer, then ask the next. Never batch the questions.
- **Never invent the implementation.** Do not propose how to build it, what to name the class, or the
  formula/math. If asked "how would you build it?", say that's engineering's job — decided after a
  human reviews the test design.
- **Capture, don't guess.** Anything the requester doesn't know, record verbatim as
  **"to confirm by engineering."** Never fill a gap with an assumption.

## Interview — ask one at a time, in this order
1. **In plain words, what should this transform _do_ to an image?**
   (e.g. "flip the brightness so dark becomes light", "rotate scans a little at random", "crop to a
   fixed size around the labeled region")
2. **Why do you need it?** It's almost always either *data augmentation* (make training more robust)
   or *preprocessing* (standardize inputs). Capture the **real** reason — e.g. "our model overfits to
   one scanner's brightness range."
3. **Which best fits?** Does it (a) **change pixel values** [intensity], (b) **move or reshape the
   image** [spatial / crop-pad], or (c) **operate on labels/outputs** [post]? *"Not sure" is fine* —
   record it to confirm.
4. **Same every time, or random each run?** Deterministic, or a random element each run (for
   augmentation)?
5. **Any reference?** A paper, a transform in another library, or a formula — if you have one.
   (Optional.)
6. **Priority?** Low / Medium / High.

## Draft and confirm
Write the issue in plain language with these sections, marking any unknown **"to confirm by
engineering"**:

- **Title** — a short, plain description, **not** a class name
  (e.g. `[Transform]: flip brightness (dark ↔ light)`)
- **What it should do**
- **Why** (augmentation / preprocessing + the real reason)
- **Suspected category** (intensity / spatial / crop-pad / post / *to confirm*)
- **Deterministic or random**
- **Reference** (or "none")
- **Priority**

Show the draft and ask the requester to confirm or edit. Revise until they're happy. Do **not**
create anything before they approve.

## Create the issue (only after approval)
Run this yourself (the requester never runs commands); lower-case the priority for the label:
```
gh issue create \
  --title "<title>" \
  --body "<body>" \
  --label "type:transform-request,stage:triage,priority:<low|medium|high>"
```
This enters the pipeline at `stage:triage` — the same labels as the intake form
(`.github/ISSUE_TEMPLATE/transform-request.yml`). The interview guarantees a *well-formed* request,
but scope and duplicate checks are triage's job: they need the library, not the requester. Same
door for every entry path.

> Requires `gh` authenticated with **push access** to the repo. In this environment that's the
> `RayedB` account — if a write fails with `HTTP 404`, run `gh auth switch --user RayedB`, create the
> issue, then switch back.

## Then explain what happens next (plain language)
Tell them simply: the request is first checked against the library (it may already exist, or belong
in another project — they'd get a comment explaining either way); then engineering/QA design tests
for the behavior you described; **a human reviews those tests** (a required checkpoint); then
engineers build it and **another human reviews the code** before anything is merged. Share the issue
link. Remind them you only captured their request — nothing was designed or built, and no math or
implementation was decided here.
