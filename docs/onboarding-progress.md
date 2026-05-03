# Onboarding Progress State

`mb` owns the durable onboarding progress contract. Agent runtimes own the
conversation and judgment around the user's answers.

## Storage

The progress file lives in the business repo:

```text
.mb/onboarding.json
```

This file is lightweight operational progress. It is meant to help a second
agent/runtime session resume without rereading a long transcript.

## State Boundary

Canonical business truth belongs in git as normal business files:

- accepted offer, audience, voice, proof, and finance summaries in `core/`;
- research notes in `research/`;
- durable choices in `decisions/`;
- campaign, document, and log artifacts in their matching folders.

`.mb/onboarding.json` stores operational progress only:

- checklist step status;
- missing input labels;
- onboarding persona such as `solo`, `small_team`, or `larger_team`;
- bounded collection guidance and the next recommended action.

Do not store secrets, credentials, raw customer/member exports, full finances,
chat transcripts, or large pasted source dumps in this file.

## Commands

Inspect progress:

```bash
mb onboard status --repo . --json
```

Create or update the lightweight plan:

```bash
mb onboard plan \
  --repo . \
  --team-size solo \
  --business-type coaching \
  --success-stage working \
  --desired-outcome "usable core reference"
```

`mb onboard` also writes the initial plan when it creates or connects a repo.

## Resume Rules

On resume, agents should:

1. run `mb onboard status --json`;
2. read the checklist and `summary.next_recommended_action`;
3. collect only the missing inputs for the current step;
4. write accepted business truth to the normal repo files;
5. run `mb onboard status --json` again to verify progress.

Solo onboarding can keep the GitHub/team layer lightweight. Small-team and
larger-team onboarding should document owners, review expectations, and where
team tasks and proposals live before the repo becomes the shared operating
surface.

## Claude Code Smoke Plan

Manual runtime smoke for onboarding resume:

1. create a fresh repo with `mb onboard --yes --name "Smoke Business" --path /tmp/mainbranch-onboard-smoke`;
2. run `mb onboard plan --repo /tmp/mainbranch-onboard-smoke --team-size small-team --business-type agency --success-stage working --desired-outcome "usable core reference"`;
3. `cd /tmp/mainbranch-onboard-smoke`;
4. run `mb onboard status --json` and confirm missing core inputs are reported;
5. launch `claude`;
6. run `/start`;
7. verify `/start` uses `mb onboard status --json` to resume and does not ask
   for full finances, credentials, or exhaustive operations details before the
   core reference exists.
