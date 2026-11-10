---
name: darshan-singh-meel-ask-me
description: Interview the user in short rounds of questions (up to 4 per prompt) to pin down requirements and a plan before coding. Use when requirements are unclear, the plan is complex or risky, there are several reasonable approaches, or the user says "grill me", "ask me questions first", or "help me think this through".
---

# Ask Me

Before writing code, interview the user until the plan is clear and agreed. The goal is to catch wrong assumptions while they're cheap to fix.

This is for planning a task. Questions go in **rounds**: up to 4 independent questions per prompt (shown as tabs); questions that depend on an answer go in the next round.

## Rules
- **Rounds, not lists:** up to 4 questions per round, only ones that don't depend on each other. Use AskUserQuestion; if unavailable, a short numbered list with options.
- **Most important first:** goal and scope → inputs/outputs → edge cases → constraints → success criteria.
- **Every question has options with a default** (see Limits), so the user can answer in one word.
- **Look it up instead of asking** when the codebase, schema, configs, docs, or existing models/DAGs can answer it — checking the `<reponame>-knowledge-graph/` folder first if it exists (index, data model, flows). Only ask what only the user knows.
- **Short questions.** One or two sentences plus your recommendation. No preamble.
- **Follow the thread:** if an answer opens a new important question, ask that next.
- **Challenge the plan:** if something seems overcomplicated, unnecessary, or risky, say so and suggest the simpler option.
- **Stop when it's clear.** Don't ask about things that don't change what gets built. If the user says "just go", stop and proceed with your recommended answers.

## Limits — don't grill forever
- **Question caps by task size — never more:**
  - **Simple: 5** — small feature, single file/model, clear scope.
  - **Medium: 8** — several files/models, new pipeline step, some unknowns.
  - **Hard: 10** — many components, schema/interface changes, production data, migrations.
- **Every question offers a default option.** Give 2–4 options with the recommended one first, marked `(default)`. Example: `Q3/8 — Late-arriving rows? A) 3-day lookback (default)  B) No lookback  C) Full reprocess weekly`. The user can reply "A", type their own answer, or just say "default".
- **Before asking, rank.** List candidate questions silently, then ask only the ones whose answer would change what gets built. Everything else → use your recommended default.
- **Show progress:** number questions across rounds (`Q5/8`), so the user knows the end is near.
- **Each question must be blocking.** Test: "If the user doesn't answer, would I likely build the wrong thing?" If no, don't ask — decide it yourself.
- **No follow-up chains on details.** At most one follow-up per topic.
- **Stop early** as soon as the remaining unknowns have safe defaults.
- **User can end it anytime:** "go", "just do it", "skip", or "use defaults" → stop immediately.
- **When the cap is hit:** stop asking, use recommended defaults for anything still open, and list them in the plan under `Defaults I chose` so the user can correct them in one reply.

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
Edge cases handled: <bullets>
Defaults I chose: <decisions made without asking — user can override>
Verify by: <tests/checks>
Open risks: <if any>
```
Ask "Good to start?" — then build it following the darshan-singh-meel-code skill.
