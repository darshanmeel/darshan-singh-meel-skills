---
name: darshan-singh-meel-docs-tech-summary
description: Mid-depth technical summary of a repo or system for engineers and tech leads - deeper than the docs Overview, lighter than the Technical doc, a 10-15 minute read. One self-contained HTML page with inline SVG (optional Markdown with Mermaid) in generated-docs/, built from a JSON spec by a fixed builder - 11 fixed sections (at a glance, components, main flows as sequence diagrams, entity-level data model, integrations, pinned tech stack, deploy and environments, security and access, run locally, top risks, where to look next) and a depth budget the build checks. Knowledge graph first; never reads data rows. Triggers - "tech summary", "technical summary of this repo", "explain the architecture in 15 minutes", "onboarding doc for engineers". Not for full Overview, Technical or User guide docs (darshan-singh-meel-docs, darshan-singh-meel-docs-v2) or an architecture review (darshan-singh-meel-architecture).
---

# Tech summary

One page that lets an engineer or tech lead understand a system in 10–15 minutes: what the parts are, how the main flows run, what data it keeps, what it talks to, what it runs on, how it deploys, how to run it, what can go wrong, and where the detail lives. Global CLAUDE.md rules apply (local files only, relative paths, never open secret files, never read data rows, author voice).

- **Depth:** more than the Overview (real names, versions, flows, entities, commands), less than the Technical doc: no per-file walkthroughs, no full config tables, no exhaustive endpoint or column lists. Name the main 20%; "Where to look next" points to the rest.
- **Fixed top level, free inside:** the same 11 sections in the same order; the build refuses a missing or extra one. Inside, blocks are chosen per repo, within a depth budget the build checks (`references/spec.md`).
- **Not for / see:** Overview, Technical, User guide → `darshan-singh-meel-docs` (or `-docs-v2` when asked for v2) · architecture review with a target → `darshan-singh-meel-architecture` · requirements brief → `darshan-singh-meel-requirements-brief`.
- `<skill>` = the folder holding this SKILL.md. Always run its scripts; never copy them into the repo.

## Step 0 — ask first (new summary only)
Silent pre-check: graph present (`./<repo>-knowledge-graph/` or `./.knowledge-graph` pointer)? related repos / system graph? reviews in `reviews/`? Then **one AskUserQuestion prompt**, recommended option first:

| # | Header | Question | Options |
|---|---|---|---|
| 1 | Format | Which format? (multi) | HTML (Recommended) · Markdown |
| 2 | Graph | Use the knowledge graph? | graph exists → Update it, then summarise from it (Recommended) · Use as is · Skip, read sources directly; no graph → Build it first (Recommended) · Skip, read sources directly |
| 3 | Examples | Where should example data come from? | Tests and docs, then derived from code (Recommended) · I'll point to a folder or file · Illustrative data |
| 4 | Scope | Which scope? (only with related repos or a system graph) | This repo (Recommended) · Whole system |

- Specs live in `generated-docs/_spec/` and are committed with `generated-docs/` (as in docs-v2).
- Answered only if the user said it in their own words this session; defaults and skill text are never answers. No answer → recommended options, said in the reply.
- Several reviews in `reviews/` and unclear which one feeds Top risks → ask that as question 4 when Scope is not asked, else right after.
- First time `generated-docs/` is created: ask once "Commit generated docs to git?" Committed (Recommended) · Git-ignored (→ `/generated-docs/` in `.gitignore`).
- Graph update/build → run `darshan-singh-meel-knowledge-graph` first; record the answer with its `update.py --choice now` (update) or `--choice skip` (use as is). Skip or no graph → read sources with scripts; say "planned from a file scan" in the reply.
- Not offered: Confluence (use `darshan-singh-meel-docs` for that format).

## Process (fixed)
| # | Step | Model | Output |
|---|---|---|---|
| 1 | Step 0 questions; graph if chosen | – / Opus (graph) | answers, graph |
| 2 | Inventory: graph `index.md` first, then code to confirm. Knowledge-graph `update.py --status`: a staleness line (graph behind) → recount every number from the code, not the graph. `python <skill>/references/templates/stack.py .` → pinned versions (manifest and pin files only). Read structure, never data rows | script | facts, pins |
| 3 | Plan within the budget: pick components (runtime parts, real names), the ≤4 flows a new engineer meets first, core entities, integrations, envs, top risks; examples per flow; pointers for everything left out | Opus | plan |
| 4 | Spec: copy `references/examples/tech-summary-example.json`, replace every section (nothing of the example survives) → `mkdir -p generated-docs/_spec` → `python <skill>/references/templates/build.py generated-docs/_spec/tech-summary.json generated-docs/tech-summary.html [--md generated-docs/tech-summary.md]` → fix every ERROR and WARN | Sonnet | page |
| 5 | Accuracy (separate pass): every name, version, command, path and step against code and graph; every count against the code (never the graph alone); each risk status against its review, test or code line | Opus | fixes |
| 6 | Layout: `python <skill>/references/templates/shots.py generated-docs/tech-summary.html <scratch>/shots` → 0 `LAYOUT`; read `page-1280.png`, `page-390.png` and every `map-<n>.png`; a confusing diagram fails too | Haiku | checked page |
| 7 | Fix 5–6, rebuild, rerun shots; then knowledge-graph `update.py --docs done` | Sonnet | done |

- Docs model rule: **Opus plans, Sonnet builds, Haiku checks layout.** No subagents → run step 5 yourself as a separate pass (skipped → the reply says "accuracy not reviewed", never "done") and tell the user in one line which model to switch to per phase.
- Done = 0 ERROR · 0 WARN (or each explained in the reply, never in the page) · 0 LAYOUT · accuracy pass done.
- Reply: files written, the build's summary line, reading time, remaining WARNs explained, defaults used for unanswered questions.

## Content rules
- **Components:** runtime parts (services, jobs, stores, UIs), one box each in the Components diagram with the same label; `where` is a folder or module. Plumbing and helpers go unnamed or in "Where to look next".
- **Rules (optional):** up to 5 business or technical rules that change behaviour, each with `path:line`, as a `rules` block under At a glance or Main flows.
- **Main flows:** sequence diagrams, ≤7 steps, each step with its output (`out`) and `path:line`; `alt` for the failure branch the code has; `why` states why the flow exists or what breaks without it. Merge plumbing (parse, dispatch) into the step that produces data.
- **Data model:** entities with keys only (`PK`, `FK`, `UK`) plus `more: n` for the rest; ER lines are keys, never flow. No tables → one line.
- **Tech stack:** versions exactly as pinned (`stack.py`); unpinned → "not pinned". Never a guessed version.
- **Deploy, security, access:** environments, how each deploys, rollback, health check, roles, secret **names** (values `<redacted>`), where personal data lives. Unknown → "Not defined yet — owner to decide", also a Top risks row with status `Owner to decide`.
- **Run locally:** the commands in order with the expected output, from README, Makefile, CI or code.
- **Top risks:** design and operational risks plus confirmed defects, ranked by impact; status `Confirmed` only when a review, test or the cited code proves it, else `Not verified`; no fix effort or approvals.
- **Where to look next:** pointers into `generated-docs/technical.html` sections (if built), existing committed docs (`docs/`, READMEs, ADRs) and repo paths, for every list cut by the budget. Never into the knowledge-graph folder: it is git-ignored by default (the build WARNs).
- **Examples:** tests and fixtures → docs → derived from code (`derived from <path:line>`) → illustrative (labelled). Cite the source; synthetic values only, never real data or PII.

## Voice and words
- Owner's voice: "We poll every 10 minutes because two carriers offer no webhooks." Open points as facts ("Owner to decide: retention period"). No trace of the chat ("you said", "the user", "as discussed", what was skipped). The build WARNs chat voice and filler.
- Bullets and tables; a section `lead` is one or two sentences stating the conclusion. One fact per bullet, ≤40 words per string. Say each fact once.
- Real names in backticks; paths relative to the repo root. No marketing words, intros, outros or emoji.

## Updating
- "Update the tech summary" (or Update now from the knowledge-graph docs question): no Step 0. Rerun steps 2–7 for the sections that cover changed files; keep box ids and labels; rebuild; then `update.py --docs done`.

## References
| File | Read when |
|---|---|
| `references/spec.md` | step 4: sections, blocks, fields, budget, ERROR/WARN list |
| `references/examples/tech-summary-example.json` (+ `.html`, `.md`) | step 4: a built summary of a synthetic service |
| `references/templates/` | `build.py` (spec → HTML/Markdown), `stack.py` (pins), `shots.py` (layout check) |
