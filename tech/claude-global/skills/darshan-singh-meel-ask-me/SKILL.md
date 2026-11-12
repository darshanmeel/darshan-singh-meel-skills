---
name: darshan-singh-meel-ask-me
description: Interview the user in short rounds of questions (up to 4 per prompt) to pin down requirements and a plan before starting an unclear or complex task (code, data model, pipeline, infra). Not for the fixed setup questions of docs, graph, review. Use when requirements are unclear, the plan is complex or risky, there are several reasonable approaches, or the user says "grill me", "ask me questions first", or "help me think this through".
---

# Ask Me

Before starting, interview the user until the plan is clear and agreed. The goal is to catch wrong assumptions while they're cheap to fix.

## Rules
- **Rounds, not lists:** up to 4 independent questions per prompt (AskUserQuestion tabs; if unavailable, a short numbered list with options). Questions that depend on an answer go in the next round.
- **Most important first:** goal and scope → inputs/outputs → edge cases → constraints → success criteria.
- **Look it up instead of asking** when the knowledge graph (if one exists, per CLAUDE.md), then code, schema, configs, docs, or existing models/DAGs can answer it. Only ask what only the user knows.
- **Short questions.** One or two sentences plus your recommendation. No preamble.
- **Follow-ups:** only if blocking, in the next round, at most one per topic.
- **Challenge the plan:** if something seems overcomplicated, unnecessary, or risky, say so and suggest the simpler option.

## Limits — don't grill forever
- **Question caps by task size — never more:**
  - **Simple: 5** — small feature, single file/model, clear scope.
  - **Medium: 8** — several files/models, new pipeline step, some unknowns.
  - **Hard: 10** — many components, schema/interface changes, production data, migrations.
- **Every question offers 2–4 options**, recommended first, marked `(Recommended)`. Example: header `Late rows`, question `Late-arriving rows?`, options `3-day lookback (Recommended)` · `No lookback` · `Full reprocess weekly`. The user can pick an option, type their own answer, or say "default".
- **Before asking, rank.** List candidate questions silently, then ask only the ones whose answer would change what gets built. Everything else → use your recommended default.
- **Show progress:** number questions across rounds (`Q5/8`; N = questions planned after ranking, ≤ cap).
- **Each question must be blocking.** Test: "If the user doesn't answer, would I likely build the wrong thing?" If no, don't ask — decide it yourself.
- **Stop early** as soon as the remaining unknowns have safe defaults.
- `"go"` · `"just do it"` · `"skip"` · `"use defaults"` · cap hit → stop; recommended defaults for the rest, listed under `Defaults I chose`.

## What to cover (only what's relevant)
- **Goal:** what problem this solves, who uses the result, what "done" looks like.
- **Scope:** what's in, what's explicitly out, what must not change.
- **Inputs & outputs:** sources, formats, schemas, expected volume.
- **Data work:** grain of each output, keys, dedup rules, NULL handling, late-arriving data, incremental vs full refresh, backfill needs, schedule and SLA.
- **Edge cases:** empty input, duplicates, failures, retries, partial runs.
- **Constraints:** performance, cost (warehouse credits/cluster size), security and access, existing patterns to follow, deadlines.
- **Interfaces:** any table/column/API/DAG changes that affect downstream users.
- **Verification:** which tests, checks, or queries will prove it works.

## Finish
When everything important is answered, write a short agreed plan:
```
Goal: <one line>
Approach: <2–4 bullets, simplest option>
Out of scope: <bullets>
Edge cases: <bullets>
Defaults I chose: <user can override>
Verify by: <tests/checks>
Open risks: <if any>
```
Ask "Good to start?" (skip the question if the user already said go: show the plan and start) — then build it following the darshan-singh-meel-code skill.

The plan goes into a file (design doc, ticket, `NOTES.md`) → rewrite it in the owner's voice (CLAUDE.md "Author voice"): "Defaults I chose" become decisions ("We use a 3-day lookback"), open risks are facts ("Not yet tested on production volumes"), no reference to the interview.
