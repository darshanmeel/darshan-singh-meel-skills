---
name: darshan-singh-meel-architecture
description: Architecture review of a repo from its knowledge graph - the current architecture, problems with path:line evidence, a proposed target built per component (keep / move / later, hybrid by default) from a kind-specific catalogue of moves (e.g. PySpark or pandas doing SQL work → Spark SQL, dbt or DuckDB; ADF or cron chains → Airflow or the platform's jobs; per-env infra copies → Terraform modules), each row with one recommended tool plus 2-3 alternatives the user can ask for instead (keep and later rows too), the target in Technical-doc shape (components, main flows, data model, configuration, security, deploy, operations, tests), current-vs-proposed workflow traces, impact on cost, performance, maintenance and tech debt, and an ordered migration - one HTML page from a JSON spec. Use only when the user asks for an architecture review, a target or better architecture, a redesign or modernisation, "is there a better way to do this", or accepts the offer made after a Technical doc; also "use <alternative> instead" on an existing review.
---

# Architecture review
Current → problems → keep/move/later → target → workflows → impact → migration, one page: `generated-docs/architecture.html` (spec `generated-docs/_spec/architecture.json`).
- **When:** only on request ("architecture review", "is there a better way", "redesign", "target architecture") or when the user accepts the one-line offer the docs skills make after a Technical doc. Never unprompted.
- **Every word carries a fact or an insight.** Lists and diagrams; no prose tables (tables only for keep/move/later, Impact, traces and docs-v2 row blocks).
- **Input → Process → Output** with the output of each step: target Main flows (4) are strips with a `why`; workflows (5) trace one case current vs proposed.
- **Every claim is evidence or a labelled estimate:** `path:line`, a `facts.json` fact, or `estimate` + assumption.
- Global CLAUDE.md rules apply (local files only, relative paths, never open secret files, never read data rows).
- `<skill>` = this folder; `<docs-v2>` = `darshan-singh-meel-docs-v2` beside it. Fields, ERROR/WARN: `references/spec.md`. Moves: `references/patterns.md`.

## Step 0 — ask first
One prompt (skip what the user already said this session):
- **Graph:** exists → Update it, then review (Recommended) · Use as is · Skip, read sources. None → Build it first (Recommended) · Skip. Record with knowledge-graph `update.py --choice now|skip` (graph read-only → skip recording, say so).
- **Review** (only if `reviews/` holds several and the newest is unclear): which one feeds Problems.
- No answer → build/update the graph, newest review; say so.

## Process (fixed)
| # | Step | Model | Output |
|---|---|---|---|
| 1 | Graph: build/update via `darshan-singh-meel-knowledge-graph` (or skip) | Opus | graph at HEAD |
| 2 | `python <docs-v2>/references/templates/inventory.py` from the repo root | script | `_spec/inventory.json` + `facts.json` (no graph → "planned from a file scan" in the reply) |
| 3 | Evidence: graph `index.md`, entry points, flows, deploy units; review Must/Should and tech debt (items already fixed in code are not problems); graph `possible_issue` notes; cost config (warehouse/cluster size, schedule, retention, instance type) | Opus | cited facts; numbers in `facts.json` → `inventory.py --check-facts` 0 MISMATCH |
| 4 | Current: L0 (3–7 boxes), components (graph nodes/edges, lanes per platform), runtime/deploy, hotspots; `current_doc` = `generated-docs/technical.html` if it exists | Opus | `current` |
| 5 | Problems: bottleneck, cost, spof, scaling, security, correctness, tech debt; `path:line` + severity | Opus | `problems` |
| 6 | **Signals → moves:** repo kind from inventory `profile`; per component, match `patterns.md` signals in graph and code; keep / move / later with evidence | Opus | `proposal.moves`, `changes[].signal`, `pattern` |
| 7 | Pick per row: stack's current feature first; else the tool that fits this repo; 2–3 current alternatives on **every** row (official docs: `patterns.md` Docs lines); `free_in` per fix; `later` rows get `until`; options 2–3, one chosen, each sized by a script (lines, tasks, tests before → after) | Opus | `tool`, `alternatives`, `free_in`, `until`, `options[].size` |
| 8 | Target in Technical shape: diagram (`new`/`changed`), new/changed `components`, Main flows (= proposed strips, `why` on changed steps), Data model · Deploy and environments · Operations (blocks, or one "Stays: …" line); Configuration · Security and access when they change; Tests whenever a tool moves (what replaces each suite) | Opus | `proposal` |
| 9 | Workflows: 2–3 real flows from the graph, current vs proposed, one trace each; ≥ 1 `typical` from an entry point to a final output; values from test fixtures | Opus | `workflows` |
| 10 | Impact per change: cost · performance · maintenance · tech debt · risk | Opus | `impact` |
| 11 | Migration: High fixes first, then quick wins; effort, risk, rollback | Opus | `migration` |
| 12 | Build: `mkdir -p generated-docs/_spec` → `python <skill>/references/templates/build.py generated-docs/_spec/architecture.json generated-docs/architecture.html` → fix every ERROR and WARN | Sonnet | page |
| 13 | Accuracy + feasibility: `build.py --checklist <spec>` → open each item, fix the spec, tick it (`- [x]`) → rebuild: "Accuracy: N of N checked" | Opus | ticked checklist |
| 14 | Layout: `python <docs-v2>/references/templates/check.py <html> generated-docs/_spec/shots` (1280 and 390 px) → 0 `LAYOUT`; `python <skill>/references/templates/shots.py <html> generated-docs/_spec/shots` → read every `map-<n>.png`, `s1…s8.png` and `p1…p8.png` (native size) | Haiku | 0 LAYOUT, shots read |

- **Done** = 0 ERROR · 0 WARN · 0 LAYOUT · checklist all ticked · shots read. Otherwise the reply says what is missing ("accuracy not reviewed", "layout not checked"), never "done".
- No subagents unless asked: run 13 as a separate pass; tell the user in one line which model to switch to per phase.
- First time `generated-docs/` is created: ask once whether to commit it. Start the spec from `references/examples/architecture-example.json`.
- Reply = the build's terminal block + "planned from a file scan", "not in git: refresh unavailable", or graph staleness if any.

## Rules for good proposals
- **No signal, no move.** A tool change cites `signal` lines showing the catalogue pattern. Never swap a tool for taste.
- **Best target stack first, then the diff:** pick the best current tool set for the whole flow, compare it with today, change only what differs. Changes travel together: a move that needs another (pandas → DuckDB + dbt needs an orchestrator, so cron → Airflow) lists it in `goes_with`; impact and migration include both. Already on that tool (Airflow present) → only the other part moves. No bridges or adapters just to keep old formats or interfaces: the migration says what changes for consumers and how to roll back.
- **Per component, hybrid by default:** keep what works (say why), move only where the signal is, `later` with what must be true first. Most components differ from the target → `redesign` with a full target; the user can also ask "show a full redesign" → add it as an option with its own size, impact and migration.
- **Current and fit → keep, nothing to suggest:** a component on a current version that fits the target gets `current: true` on its keep row (rendered "current, fits"), no alternatives, no impact rows. Newer is not a signal; a move needs a problem, an EOL/deprecated version, or a cited gain.
- **Simplest change that removes the problem:** config → code → new component → new platform. The stack's current features at the pinned versions first.
- **Pick + alternatives on every row:** a move names one tool with why it fits *this* repo; every row, `keep` and `later` included (scheduler, compute, deploy, incremental mode, tests, DQ), lists 2–3 current alternatives with one trade-off each, so the user can say "use <alternative> instead". Versions, product names and features from official docs when unsure (names change: say the page in `source` or a question).
- **Free in target:** per fix on the current engine, set `free_in` when the target tool provides it built in (null-safe merge, latest-per-key, run order, lineage, tests, retries); the checklist asks it of every fix left unset. ≥ 3 free → `move` (`later` only with an `until` someone can check); never keep the old engine and rebuild those by hand.
- **Size both options:** a script counts what a move replaces (lines, tasks, tests); estimate the target (SQL models ~20–40 lines each plus macros). A rewrite listed with costs only makes evolve look cheaper than it is. An option that ends smaller in lines and tasks wins unless the chosen one gives `why_not`: a blocker checked in the docs.
- **A blocker is checked, not assumed:** before "the tool cannot do X" (dynamic schema, nested flattening, merge rules), read the adapter's docs and name the page. "Unchecked", "not verified" or "if its … is" in a later row, option or question → WARN: check now.
- **Rewrites run in parallel** (`parallel-run-cutover`): separate schema, compare counts and keys, cut over by a committed value. A defect kept for parity is logged (`dq-side-table`) and listed in questions.
- **"No run history" is not a reason to keep** compute: make serverless a `later` with a measure-first step.
- **Cost from real config:** size × run time × schedule, storage × retention; cite the file. No cost config in the repo → say "no cost config in repo"; estimates with ranges only. Shared compute (a warehouse other jobs use) → attribute only this job's share. A change that raises cost says `rises: …`.
- **Measured** = the number is in the cited line or a fact; run, restart and wait times are estimates. A measured `now` with a design consequence (no counted saving) shows as "now measured · effect by design".
- **Tech debt** from review §12 items (duplicated logic, EOL versions, hard-coded config, manual steps, dead paths, contract drift).
- **Every High problem gets a change** or `accept`. Verdict: none High → `keep`; same stack, parts changed → `evolve`; core structure changes → `redesign`.
- **Feasibility (what step 13 checks):** every consumer of a changed thing is handled (client routes need SPA fallback, CORS origins, ports, roles, schedules); a leaked secret is **rotated**, not moved, and stateful stores change explicitly (e.g. a DB role password on an initialised volume); terms of art exact (HS256 is symmetric: one shared secret); cite the line that does the thing, not a caller; dates and deprecation schedules only with a source; partial changes say what they leave out; a saving resting on platform behaviour lists it under questions or assumptions; the chosen change carries its own risks (not only the rejected option); a documented process nobody enforces is "not enforced", not "missing".
- **Migration:** each step ships and rolls back alone; High fixes first, then quick wins (S, Low), unless `needs` or `wait` says why; a step that changes how something starts goes after the step it depends on.
- Workflows are real flows (`flows`, entry points): one `typical` run end to end (landing → final output), then edge or failure cases; values from tests, fixtures or docs; `synthetic: true` only where none fits (all synthetic while the repo has tests → WARN). A failure trace may have a shorter proposed strip.

- **Incremental pipelines:** cover `patterns.md` "Target checklist" (in-batch dedup + tie-breaker, cursor, deletes as two options, DQ sink, packaging).
- **No user to ask** (a subagent or batch run): use the Step 0 recommended defaults and say so in the reply.

## Updating
- **"Use <alternative> instead"** (no questions): `python <skill>/references/templates/build.py --use <spec> <C-id|M-n> "<alternative>"` (`M-n` = the table row) → the alternative becomes the pick, the old pick (the change's tool, the row's `to`, or a keep row's `now`) an alternative, TODOs mark the two texts to write. A row swap clears the row's `change`: add a change for the move (tool, signal, pattern, impact, migration step). It prints `rewrite` for every text naming the old pick (short names too: "MWAA") and `check` for every text tied to the change → rewrite moves row, target diagram, components, Main flows, technical sections, workflows, impact, migration and options for the new tool (its current features from official docs) → rebuild (WARN while a tied text names an alternative) → `--checklist`, tick the items that lost their tick → `check.py` + `shots.py`.
- **A tool not in the list** ("use Prefect"): check its fit in its official docs; fits → add it to that row's or change's alternatives (replacing the weakest), then `--use`; no fit → say why in one line.
- **"Update the architecture review"** (or `docs_pending` lists `architecture.html`): no Step 0; update the graph if stale, rerun `inventory.py`, `build.py --changed <spec> <html>` → re-check the sections and citations it prints (steps 13–14 for those), rebuild, then knowledge-graph `update.py --docs done architecture.html`.
- A new or removed High problem → redo steps 5–11 for it; the verdict may change.
