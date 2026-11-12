---
name: darshan-singh-meel-ask-me
description: Interview the user in short rounds of questions (up to 4 per prompt) to pin down requirements and a plan before starting an unclear or complex task (code, data model, pipeline, infra). Not for the fixed setup questions of docs, graph, review. Use when requirements are unclear, the plan is complex or risky, there are several reasonable approaches, or the user says "grill me", "ask me questions first", or "help me think this through".
---

# Ask me
Pin the plan before code; catch wrong assumptions while cheap.

## Rounds
- ≤4 independent questions per round (AskUserQuestion tabs; else numbered list). Dependent questions → next round.
- Order: goal/scope → inputs/outputs → edge cases → constraints → success criteria.
- Each question: 1–2 lines, 2–4 options, rec first marked `(Recommended)`. Number across rounds: `Q5/8` (N = questions planned after ranking, ≤ cap).
  e.g. header `Late rows` · `Late-arriving rows?` · `3-day lookback (Recommended)` · `No lookback` · `Full reprocess weekly`. Reply: option · own text · "default".
- Knowledge graph first if one exists (CLAUDE.md), then code · schema · configs · docs can answer it → look it up, don't ask.
- Challenge: overbuilt, unnecessary, risky → say so, offer simpler.

## Limits
- Cap: simple 5 (1 file/model, clear scope) · medium 8 (several files, new pipeline step, unknowns) · hard 10 (many components, schema/interface change, prod data, migration).
- Ask only blocking questions: "unanswered → likely build wrong thing?" No → decide yourself.
- Rank silently first. Follow-ups: only if blocking, next round, ≤1 per topic. Stop early when the rest have safe defaults.
- `"go"` · `"just do it"` · `"skip"` · `"use defaults"` · cap hit → stop; rec defaults for the rest, listed under `Defaults I chose`.

## Cover (only what's relevant)
Goal (problem, user, done) · scope (in, out, must not change) · inputs/outputs (sources, formats, schemas, volume) · data (grain, keys, dedup, NULLs, late data, incremental vs full, backfill, schedule, SLA) · edge cases (empty, duplicates, failures, retries, partial runs) · constraints (performance, cost, security/access, patterns, deadlines) · interfaces affecting others (table/column/API/DAG) · verification.

## Finish
```
Goal: <1 line>
Approach: <2–4 bullets, simplest>
Out of scope: <bullets>
Edge cases: <bullets>
Defaults I chose: <user can override>
Verify by: <tests/checks>
Open risks: <if any>
```
"Good to start?" (user already said go → skip; show plan, start) → build with `darshan-singh-meel-code`.
- Plan into a file (design doc · ticket · `NOTES.md`) → owner's voice (CLAUDE.md "Author voice"): defaults → decisions ("We use a 3-day lookback") · risks → facts ("Not yet tested on production volumes") · no reference to the interview.
