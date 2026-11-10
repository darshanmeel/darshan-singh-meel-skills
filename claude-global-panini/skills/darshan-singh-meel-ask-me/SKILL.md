---
name: darshan-singh-meel-ask-me
description: Interview the user in short rounds of questions (up to 4 per prompt) to pin down requirements and a plan before coding. Use when requirements are unclear, the plan is complex or risky, there are several reasonable approaches, or the user says "grill me", "ask me questions first", or "help me think this through".
---

# Ask me
Pin the plan before code; catch wrong assumptions while cheap.

## Rounds
- ≤4 independent questions per round (AskUserQuestion tabs; else numbered list). Dependent questions → next round.
- Order: goal/scope → inputs/outputs → edge cases → constraints → success criteria.
- Each question: 1–2 lines, 2–4 options, rec first marked `(default)`. Number across rounds: `Q5/8`.
- Graph · code · schema · configs · docs can answer it → look it up, don't ask.
- Challenge: overbuilt, unnecessary, risky → say so, offer simpler.

## Limits
- Cap: simple 5 · medium 8 · hard 10 (many components, schema/interface change, prod data, migration).
- Ask only blocking questions: "unanswered → likely build wrong thing?" No → decide yourself.
- Rank silently first. ≤1 follow-up per topic. Stop early when the rest have safe defaults.
- "go" · "just do it" · "skip" · "use defaults" → stop now.
- Cap hit → stop; defaults for the rest.

## Cover (only what's relevant)
Goal · scope (in, out, must not change) · inputs/outputs (sources, formats, schemas, volume) · data (grain, keys, dedup, NULLs, late data, incremental vs full, backfill, schedule, SLA) · edge cases · constraints (performance, cost, access, patterns, deadlines) · interfaces affecting others · verification.

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
"Good to start?" → build with `darshan-singh-meel-code`.
