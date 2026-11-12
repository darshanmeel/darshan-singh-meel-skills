---
name: darshan-singh-meel-architecture
description: Architecture review of a repo from its knowledge graph - the current architecture, problems with path:line evidence, a proposed target built per component (keep / move / later, hybrid) from a kind-specific catalogue of moves (e.g. PySpark or pandas doing SQL work → Spark SQL, dbt or DuckDB; ADF or cron chains → Airflow or the platform's jobs; per-env infra copies → Terraform modules), one recommended tool plus 2-3 alternatives on every row, the target in Technical-doc shape (components, main flows, data model, configuration, security, deploy, operations, tests), current-vs-proposed traces, impact on cost, performance, maintenance and tech debt, and an ordered migration - one HTML page from a JSON spec. Use only when the user asks for an architecture review, a target or better architecture, a redesign, "is there a better way to do this", or accepts the offer made after a Technical doc; also "use <alternative> instead" on an existing review. Not for requirements briefs (darshan-singh-meel-requirements-brief).
---

# Architecture review
Current → problems → keep/move/later → target → workflows → impact → migration → one page `generated-docs/architecture.html` (spec `generated-docs/_spec/architecture.json`).
- When: on request only ("architecture review" · "is there a better way" · redesign · target) or the user accepts the docs skills' one-line offer after a Technical doc. Never unprompted.
- Each word = fact or insight. Lists + diagrams; no prose tables (only keep/move/later · Impact · traces · docs-v2 row blocks).
- Input → Process → Output, output per step: target Main flows (4) = strips + `why`; workflows (5) = one trace current vs proposed.
- Each claim = `path:line` · `facts.json` fact · `estimate` + assumption.
- CLAUDE.md applies (local only · relative paths · no secret files · no data rows · author voice: page = architect's own, open points as facts, no chat).
- `<skill>` = this folder; `<docs-v2>` = sibling `darshan-singh-meel-docs-v2`. Fields, ERROR/WARN → `references/spec.md`. Moves → `references/patterns.md`.

## Step 0 — ask
One prompt (skip what user said this session):
- Graph: exists → Update, then review (Rec) · Use as is · Skip. None → Build first (Rec) · Skip. Record: knowledge-graph `update.py --choice now|skip` (read-only graph → skip, say so).
- Review: only if `reviews/` has several, newest unclear.
- No answer → build/update graph, newest review; say so.

## Process (fixed)
1. Graph → `darshan-singh-meel-knowledge-graph` (Opus) or skip.
2. `python <docs-v2>/references/templates/inventory.py` (repo root) → `_spec/inventory.json` + `facts.json`. No graph → "planned from a file scan".
3. Evidence (Opus): graph `index.md` · entry points · flows · deploy units · review Must/Should + tech debt (fixed in code → not a problem) · `possible_issue` · cost config. Numbers → `facts.json` + `how`; `inventory.py --check-facts` → 0 MISMATCH.
4. Current (Opus): L0 3–7 boxes · components (lanes per platform) · runtime/deploy · hotspots · `current_doc` = `generated-docs/technical.html` if present.
5. Problems (Opus): bottleneck · cost · spof · scaling · security · correctness · tech debt; `path:line` + sev.
6. Signals → moves (Opus): kind from inventory `profile`; per component match `patterns.md` signals → keep · move · later; `signal` + `pattern`.
7. Pick (Opus): stack's current feature first; else tool fitting this repo · 2–3 current alternatives on **every** row (official docs: `patterns.md` Docs lines) · `free_in` per fix · `later` → `until` · options 2–3, one chosen, each sized by script (lines · tasks · tests, before → after).
8. Target, Technical shape (Opus): diagram (`new`/`changed`) · new/changed `components` · Main flows = proposed strips, `why` on changed steps · Data model · Deploy and environments · Operations (blocks, or one "Stays: …" line) · Configuration · Security and access when changed · Tests when a tool moves (what replaces each suite).
9. Workflows (Opus): 2–3 real flows, current vs proposed, one trace each; ≥ 1 `typical`, entry point → final output; values from fixtures.
10. Impact (Opus): per change · cost · performance · maintenance · tech debt · risk.
11. Migration (Opus): High fixes first → quick wins · effort · risk · rollback.
12. Build (Sonnet): `mkdir -p generated-docs/_spec` → `python <skill>/references/templates/build.py generated-docs/_spec/architecture.json generated-docs/architecture.html` → fix all ERROR + WARN.
13. Accuracy + feasibility + voice (Opus): `build.py --checklist <spec>` → open each item, fix spec, tick `- [x]` → rebuild → "Accuracy: N of N checked".
14. Layout (Haiku): `<docs-v2>/references/templates/check.py <html> generated-docs/_spec/shots` (1280 + 390 px) → 0 LAYOUT; `<skill>/references/templates/shots.py <html> generated-docs/_spec/shots` → read every `map-<n>.png`, `s1…s8.png`, `p1…p8.png`.
- Done = 0 ERROR · 0 WARN · 0 LAYOUT · checklist ticked · shots read. Else reply names what is missing ("accuracy not reviewed", "layout not checked"), never "done".
- No subagents unless asked: 13 = own separate pass; tell user model per phase, one line.
- First `generated-docs/` → ask once to commit. Start from `references/examples/architecture-example.json`.
- Reply = build's terminal block + "planned from a file scan" · "not in git: refresh unavailable" · graph staleness.

## Good proposals
- No signal → no move. Tool change cites `signal` lines of the catalogue pattern; never taste.
- Best target stack first → change only what differs. Moves that need each other → `goes_with` (pandas → DuckDB + dbt needs an orchestrator: cron → Airflow); Airflow already there → only pandas moves. No bridges to keep old formats: migration says what consumers see + rollback.
- Per component, hybrid default: keep what works (why) · move where the signal is · later + what must be true first. Most components differ → `redesign`, full target. "Show a full redesign" → add it as an option (size, impact, migration).
- Current version + fits → keep, `current: true`, no alternatives, no impact rows. Newer ≠ signal; a move needs a problem, EOL, or a cited gain.
- Simplest fix: config → code → component → platform. Current features of pinned versions first.
- Pick + alternatives, every row: move → one tool, why it fits *this* repo; every row incl. keep + later (scheduler · compute · deploy · incremental mode · tests · DQ) → 2–3 current alternatives, one trade-off each → user may say "use <alternative> instead". Names, versions, features → official docs when unsure (page in `source` or a question).
- Free in target: per fix on the old engine, `free_in` = target tool that has it built in (null-safe merge · latest-per-key · run order · lineage · tests · retries). Checklist asks it of every unset fix. ≥ 3 → `move` (`later` only + checkable `until`); never rebuild by hand.
- Size both options: script counts what a move replaces (lines · tasks · tests); target estimate (SQL model ~20–40 lines + macros). Rewrite with costs only → evolve looks cheaper than it is. Smaller option (lines + tasks) not chosen → chosen needs `why_not` (blocker, docs page).
- Blocker checked, not assumed: "tool cannot do X" (dynamic schema · nested flattening · merge rules) → adapter docs first, page named. "Unchecked" · "not verified" · "if its … is" in later row, option, question → WARN: check now.
- Rewrite → parallel run (`parallel-run-cutover`): own schema · compare counts + keys · cut over by committed value. Defect kept for parity → logged (`dq-side-table`) + in questions.
- "No run history" ≠ reason to keep compute → serverless as `later` + measure first.
- Cost from real config (size × run time × schedule, storage × retention; cite file). None → "no cost config in repo", ranges only. Shared compute → this job's share only. Rise → `rises: …`.
- Measured = number in the cited line or a fact; run, restart, wait times = estimate. Measured `now` + design consequence (no counted saving) → "now measured · effect by design".
- Tech debt ← review §12 (duplication · EOL versions · hard-coded config · manual steps · dead paths · contract drift).
- Each High → a change or `accept`. Verdict: no High → `keep`; same stack, parts changed → `evolve`; core changes → `redesign`.
- Feasibility (step 13): every consumer of a change handled (SPA fallback · CORS origins · ports · roles · schedules) · leaked secret rotated, not moved; stateful stores changed explicitly (DB role password on an initialised volume) · terms exact (HS256 = one shared secret) · cite the line that does it, not a caller · dates/deprecations only with source · partial change says what it leaves out · saving on platform behaviour → questions/assumptions · chosen change carries its own risks · documented-but-unenforced = "not enforced", not "missing".
- Migration: each step ships + rolls back alone; High fixes → quick wins, unless `needs`/`wait`; a step changing how something starts after what it depends on.
- Workflows = real flows (`flows`, entry points): one `typical` run end to end, then edge/failure; values from tests/fixtures/docs; `synthetic: true` only where none fits (all synthetic + repo has tests → WARN). Failure trace may shorten the proposed strip.

- Incremental pipelines → `patterns.md` "Target checklist" (batch dedup + tie-breaker · cursor · deletes: 2 options · DQ sink · packaging).
- No user to ask (subagent/batch) → Step 0 defaults, say so.

## Updating
- "Use <alternative> instead" (no questions): `build.py --use <spec> <C-id|M-n> "<alternative>"` (`M-n` = table row) → pick ↔ alternative (old pick = change's tool · row's `to` · keep row's `now`), two TODOs; row swap clears `change` → add the move's change (tool · signal · pattern · impact · migration step). Prints `rewrite` (texts naming the old pick, short names too: "MWAA") + `check` (texts tied to the change) → rewrite moves row · diagram · components · Main flows · technical sections · workflows · impact · migration · options (new tool's current features, official docs) → rebuild (WARN while a tied text names an alternative) → `--checklist`, tick what lost its tick → `check.py` + `shots.py`.
- Tool not listed ("use Prefect"): fit checked in its official docs → fits: add to alternatives (replace weakest), then `--use` · no fit: why, one line.
- "Update the architecture review" (or `docs_pending` lists `architecture.html`): no Step 0; stale graph → update; rerun `inventory.py`; `build.py --changed <spec> <html>` → re-check printed sections and citations (13–14) → rebuild → knowledge-graph `update.py --docs done architecture.html`.
- New or removed High → redo 5–11 for it; verdict may change.
