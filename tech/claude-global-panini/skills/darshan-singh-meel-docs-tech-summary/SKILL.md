---
name: darshan-singh-meel-docs-tech-summary
description: Tech summary — mid-depth technical doc of a repo or system for engineers and tech leads; deeper than the docs Overview, lighter than the Technical doc, 10-15 min read. One self-contained HTML page, inline SVG (opt. Markdown + Mermaid) in generated-docs/, from a JSON spec by a fixed builder; 11 fixed sections (at a glance · components · main flows as sequence diagrams · entity-level data model · integrations · pinned tech stack · deploy and environments · security and access · run locally · top risks · where to look next) + a depth budget the build checks. Graph first; never data rows. Triggers - "tech summary", "technical summary of this repo", "explain the architecture in 15 minutes", "onboarding doc for engineers". Not for full Overview / Technical / User guide docs (darshan-singh-meel-docs, darshan-singh-meel-docs-v2) or an architecture review (darshan-singh-meel-architecture).
---

# Tech summary
One page, 10–15 min: parts · main flows · data kept · what it talks to · runs on · deploy · run locally · what can go wrong · where the detail lives. Global CLAUDE.md applies (local files · relative paths · no secret files · no data rows · author voice).
- Depth: > Overview (real names · versions · flows · entities · commands), < Technical (no per-file walkthroughs · no full config tables · no exhaustive endpoint/column lists). Main 20%; rest → "Where to look next".
- Fixed top level, free inside: 11 sections, fixed order; missing/extra → build refuses. Blocks per repo, within the budget the build checks (`references/spec.md`).
- Not for / see: Overview · Technical · User guide → `darshan-singh-meel-docs` (v2 asked → `-docs-v2`) · architecture review → `darshan-singh-meel-architecture` · requirements brief → `darshan-singh-meel-requirements-brief`.
- `<skill>` = this folder. Its scripts only, never a repo copy.

## Step 0 — ask (new summary only)
Pre-check (silent): graph (`./<repo>-knowledge-graph/` or `./.knowledge-graph`)? related repos / system graph? `reviews/`? → one AskUserQuestion, rec first:
| # | Header | Question | Options |
|---|---|---|---|
| 1 | Format | Which format? (multi) | HTML (rec) · Markdown |
| 2 | Graph | Use the knowledge graph? | exists → Update, then summarise from it (rec) · As is · Skip, read sources; none → Build first (rec) · Skip, read sources |
| 3 | Examples | Where should example data come from? | Tests and docs, then derived from code (rec) · I'll point to a folder or file · Illustrative |
| 4 | Scope | Which scope? (only related repos / system graph) | This repo (rec) · Whole system |
- Specs → `generated-docs/_spec/`, committed with `generated-docs/` (as docs-v2).
- Answer = user's words this session, never defaults · skill text. No answer → rec, said in reply.
- Several reviews, unclear which feeds Top risks → Q4 (no Scope) else right after.
- `generated-docs/` new → ask once "Commit generated docs to git?" Committed (rec) · Git-ignored (→ `/generated-docs/` in `.gitignore`).
- Graph update/build → `darshan-singh-meel-knowledge-graph` first; record `update.py --choice now` (update) · `--choice skip` (as is). Skip / no graph → scripts over sources; reply "planned from a file scan".
- Confluence ∉ → `darshan-singh-meel-docs`.

## Process (fixed)
| # | Step | Model | Output |
|---|---|---|---|
| 1 | Step 0; graph if chosen | – / Opus (graph) | answers, graph |
| 2 | Inventory: graph `index.md` → code confirms. Graph `update.py --status`: staleness line (behind) → every number recounted from code. `python <skill>/references/templates/stack.py .` → pins (manifest + pin files only). Structure, never data rows | script | facts, pins |
| 3 | Plan in budget: components (runtime, real names) · ≤4 flows a new engineer meets first · core entities · integrations · envs · top risks · examples per flow · pointers for the rest | Opus | plan |
| 4 | Spec: copy `references/examples/tech-summary-example.json`, replace every section (nothing survives) → `mkdir -p generated-docs/_spec` → `python <skill>/references/templates/build.py generated-docs/_spec/tech-summary.json generated-docs/tech-summary.html [--md generated-docs/tech-summary.md]` → fix every ERROR + WARN | Sonnet | page |
| 5 | Accuracy (separate pass): name · version · command · path · step vs code + graph; every count vs code (never graph alone); risk status vs its review · test · code line | Opus | fixes |
| 6 | Layout: `python <skill>/references/templates/shots.py generated-docs/tech-summary.html <scratch>/shots` → 0 `LAYOUT`; read `page-1280.png` · `page-390.png` · every `map-<n>.png`; confusing diagram = fail | Haiku | checked page |
| 7 | Fix 5–6 → rebuild → shots again → graph `update.py --docs done` | Sonnet | done |
- Docs rule: **Opus plans · Sonnet builds · Haiku checks layout.** No subagents → step 5 yourself, separate pass (skipped → reply "accuracy not reviewed", never "done"); one line: which model per phase.
- Done = 0 ERROR · 0 WARN (or each explained in reply, never page) · 0 LAYOUT · accuracy done.
- Reply: files · build summary line · reading time · WARNs explained · defaults used.

## Content
- Components: runtime parts (services · jobs · stores · UIs); one box each, same label; `where` = folder/module. Plumbing → unnamed or "Where to look next".
- Rules (opt.): ≤5 behaviour-changing rules, each `path:line`, `rules` block under At a glance / Main flows.
- Main flows: sequence diagrams, ≤7 steps; each step `out` + `path:line`; `alt` = failure branch in code; `why` = why it exists / what breaks without it. Plumbing (parse, dispatch) → merged into the data-producing step.
- Data model: keys only (`PK` · `FK` · `UK`) + `more: n`; ER lines = keys, never flow. No tables → one line.
- Tech stack: versions as pinned (`stack.py`); unpinned → "not pinned"; never guessed.
- Deploy · security · access: envs · deploy per env · rollback · health check · roles · secret **names** (values `<redacted>`) · where personal data lives. Unknown → "Not defined yet — owner to decide" + Top risks row `Owner to decide`.
- Run locally: commands in order + expected output (README · Makefile · CI · code).
- Top risks: design/operational risks + confirmed defects, by impact; `Confirmed` only when review · test · cited code proves it, else `Not verified`; no fix effort, no approvals.
- Where to look next: `generated-docs/technical.html` sections (if built) · committed docs (`docs/`, READMEs, ADRs) · repo paths, for every list cut by the budget. Never the graph folder (git-ignored; build WARNs).
- Examples: tests/fixtures → docs → derived from code (`derived from <path:line>`) → illustrative (labelled). Source cited; synthetic only, no real data, no PII.

## Voice
- Owner's voice: "We poll every 10 minutes because two carriers offer no webhooks." Open points = facts ("Owner to decide: retention period"). No chat trace ("you said" · "the user" · "as discussed" · skipped). Build WARNs voice + filler.
- Bullets + tables; `lead` = 1–2 sentences, the conclusion. One fact per bullet, ≤40 words per string, each fact once.
- Names in backticks; paths repo-relative. No marketing words · intros · outros · emoji.

## Updating
- "Update the tech summary" / graph docs question Update now → no Step 0; steps 2–7 for sections covering changed files; keep box ids + labels; rebuild → `update.py --docs done`.

## References
| File | When |
|---|---|
| `references/spec.md` | step 4: sections · blocks · fields · budget · ERROR/WARN |
| `references/examples/tech-summary-example.json` (+ `.html`, `.md`) | step 4: built summary, synthetic service |
| `references/templates/` | `build.py` (spec → HTML/Markdown) · `stack.py` (pins) · `shots.py` (layout) |
