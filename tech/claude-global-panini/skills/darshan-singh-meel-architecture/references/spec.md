# Architecture spec — input to build.py
`<skill>` = this skill's folder. Run from the repo root:
`python <skill>/references/templates/build.py generated-docs/_spec/architecture.json generated-docs/architecture.html`
- Reads `inventory.json` and `facts.json` next to the spec (docs-v2 `inventory.py`), the graph's `meta.json` (commit), `reviews/`.
- Optional: `darshan-singh-meel-docs-v2` beside this skill (flow renderer, Input → Process → Output strips, style, layout check). Missing or incompatible → `note:`, built-in style, diagrams and strips as text lists, `Layout not checked`.
- Prints the terminal reply (verdict, top 3 changes with headline impact, counts, report path), then `built <out>: N problems, N changes, N WARN`.
- Layout: `python <docs-v2>/references/templates/check.py generated-docs/architecture.html generated-docs/_spec/shots` (1280 and 390 px) → 0 `LAYOUT`; then `python <skill>/references/templates/shots.py generated-docs/architecture.html generated-docs/_spec/shots` → `s1…s8.png` (each section at 1280 px, native size) and `p1…p8.png` (each section at 390 px).
- Accuracy: `build.py --checklist <spec>` writes `architecture-checklist.md` next to the spec (one `- [ ]` per citation, change, signal, prereq, pick, free-in, moves row, option size, workflow, impact row, migration step, the page's voice, and per move/later target "fixes without `free_in` checked against its docs"; each ends in `#hash` of what it checks, plus the picks it depends on, so an edited or reordered item, or a swapped pick, loses its tick). The build prints `Accuracy: N of M checked` (no file: `not reviewed`) and WARNs on unticked items.
- Swap a pick: `build.py --use <spec> <C-id|M-n> "<alternative>"` (`M-n` = moves row n, shown in the table) → rewrites the spec (pick ↔ alternative, two `TODO` texts; the change's moves row `to` follows; a keep or later row becomes a move, its `change` cleared: add the change for the move) and prints `rewrite <json path>: …` for every text naming the old pick (any of its forms: "Amazon MWAA" also "MWAA") and `check <where>: …` for every other text tied to the change. Old pick = the change's tool, a move/later row's `to`, a keep row's `now`. Not an alternative → ERROR with how to add one. `TODO` anywhere → ERROR.
- Refresh: `python <skill>/references/templates/build.py --changed <spec> <out.html>` → `<section>: <path> changed since <commit>` per cited file changed since the page's `repo-commit`. Not in git → `note:`; no stamp, no refresh.
- Inputs sit next to the spec by design (`generated-docs/_spec/`, shared with docs-v2): never a second copy elsewhere.
- Start from `examples/architecture-example.json`. Builder tests: `python <skill>/tests/run.py`.

## Fields
```json
{"title": "Architecture: <repo>", "date": "YYYY-MM-DD",
 "subtitle": "<stack> · <schedule> · <source> → <outputs>",
 "review": "reviews/<newest review>.html",
 "verdict": "keep | evolve | redesign",
 "summary": "one line: why this verdict",
 "top": ["C1", "C2", "C3"],
 "current": {"lead": "…", "l0": {flow}, "components": {flow},
             "runtime": [["Scheduler", "text", "path:line"]],
             "hotspots": [{"what", "value", "kind", "source|fact|assumption"}]},
 "current_doc?": "generated-docs/technical.html",
 "problems": [{"id": "P1", "title", "area", "sev", "evidence": ["path:line"], "detail", "cost?", "accept?"}],
 "proposal": {"lead": "…",
              "moves": [{"component", "now", "decision": "keep|move|later", "to?", "change?": "C1", "why", "until?", "current?": true, "alternatives?": [{"name", "tradeoff"}]}],
              "diagram": {flow}, "components?": [["name", "responsibility", "where"]], "stays": ["…"],
              "technical": {"Data model": [blocks] | "Stays: …", "Configuration?": …, "Security and access?": …, "Deploy and environments": …, "Operations": …, "Tests?": …},
              "changes": [{"id": "C1", "title", "what", "why", "fixes": ["P1"], "prereq?": ["…"],
                           "pattern?": "<patterns.md id>", "signal?": ["path:line"],
                           "tool?": {"name", "why"}, "alternatives?": [{"name", "tradeoff"}], "free_in?": "<target tool>", "goes_with?": ["C2"]}],
              "options": [{"name", "what", "gains", "costs", "size", "chosen?", "why_not?"}]},
 "workflows": [{"title": "<input> → <output>", "changes": ["C1"], "needs?": ["C6"], "current": {ipo}, "proposed": {ipo}}],
 "impact": [{"change": "C1", "dim", "now", "proposed", "saving", "kind", "source?", "fact?", "assumption?", "headline?"}],
 "migration": [{"step", "changes": ["C1"], "effort", "risk", "rollback", "needs?": [1]}],
 "questions": ["…"], "assumptions": [["assumption", "why it matters"]]}
```
| Field | Rule |
|---|---|
| `verdict` | `keep` = architecture fits, small changes only (no High problem, no L step) · `evolve` = same stack, changed parts · `redesign` = core structure changes (needs a High problem) |
| `top` | ≤ 3 change ids for Summary; default the first 3. Headline = the change's impact row with `headline: true`, else its first row |
| `current.l0` | big picture: one row of 3–7 boxes, no lanes |
| `current.components` | from the graph: boxes = graph nodes (real names), arrows = its edges, lanes per platform (≤ 12 characters) |
| `runtime` | `[label, text]` or `[label, text, path:line]`: scheduler, compute, storage, deploy |
| `hotspots` | where time and cost go: `value` + basis (below) |
| `area` | `bottleneck` · `cost` · `spof` · `scaling` · `security` · `correctness` (wrong or lost data) · `tech_debt` |
| `sev` | `High` (outage, data loss, security hole, cost that grows with history) · `Medium` (cost or effort that grows) · `Low` |
| `evidence` | ≥ 1 `path:N` or `path:N-M`, checked against the repo; secret files by path only |
| `accept` | why a problem stays without a change (silences the High-without-change WARN) |
| `moves` | one row per component: `keep` (why it stays; `change` if tuned in place) · `move` (`to` + `change` required) · `later` (`to`, why, `until` = a condition someone can check: a number, a date, a docs page). A `move` row's change names the `tool` (else WARN). `alternatives` (2–3 {name, tradeoff}) on every row: tools the user can ask for instead, keep and later too (a move row may take them from its change's `tool`). `current: true` = a keep row already on a current version that fits the target: no alternatives needed, shown "current, fits"; on a move or later row → ERROR. Rendered as the one keep/move/later table, rows `M1…`, with "Until:" and "Alternatives:" lines |
| `changes` | each `fixes` ≥ 1 problem (or, required by another change, has `goes_with` instead) and has ≥ 1 impact row; ids `C1…`. A tool switch adds `tool` {name, why it fits this repo}, 2–3 `alternatives` {name, tradeoff} (not the pick), `signal` (≥ 1 `path:N`), `pattern` (a `patterns.md` id) and a `moves` row with `decision: move`. `prereq` = what else must change or hold (rendered "Also needs"). `goes_with` = other changes this one needs to work (dbt → an orchestrator), rendered "Goes with"; unknown id → ERROR. `free_in` = a target tool that provides this fix built in (≥ 3 for one tool without a move row to it, or a later row with `until` → WARN). Texts tied to a change (its moves row, impact proposed/saving, migration steps, proposed strips, chosen option) naming one of its alternatives → WARN |
| `components` | target only: new or changed rows `[name, responsibility, where]` (`where` of a new file: planned path + "(new)"); docs-v2 `components` block |
| `technical` | the target's Technical-doc sections, each docs-v2 blocks (Data model: text, er, views, bullets · Configuration: config, text, bullets · Security and access: access, text, bullets · Deploy and environments: flow, steps, io, environments, bullets · Operations: io, symptoms, tasks, bullets · Tests: tests, text, bullets) or one line saying it stays. Data model, Deploy, Operations always; Tests once a change has a `tool`; the other two when they change. `er`/`flow` need a title; ids come from the build |
| `current_doc` | the repo's Technical doc, shown as "Current design in full" |
| `diagram` (proposal) | tag added or altered boxes `new` / `changed` |
| `options` | 2–3, exactly one `chosen: true`; `gains` and `costs` = the trade-off; `size` = lines, tasks and tests before → after (script count + estimate, written "N lines, M tasks → …"), never a rewrite with costs only. Another option ending smaller in lines and tasks → WARN unless the chosen one has `why_not` (the blocker, its docs page; rendered "Why not smaller") |
| `workflows` | 2–3 real flows, ≥ 1 with a `typical` trace from an entry point to a final output; `changes` alter the flow, `needs` are changes those depend on (rendered "needs"); `current` and `proposed` are docs-v2 ipo blocks: `input`, `steps [{do ≤ 8 words, out ≤ 12, why?, where?}]` (≤ 7), `output`, `examples` = one trace `{case, title, expect, in, at, out, source?, synthetic?}`, `at` one value per step (`"="` unchanged, `null` not reached). The proposed strip (with `why` on changed steps) renders in section 4 as Main flow 4.k; section 5 shows the current strip + trace and the proposed trace |
| `dim` | `cost` · `performance` · `maintenance` · `tech_debt` · `risk` |
| `kind` | `measured`: read from code, config, graph or tests → `source` (`path:line`) or `fact` (a `facts.json` name; its value must appear in now/proposed/saving); shown "measured" only when `saving` holds a counted number, else "now measured · effect by design" · `estimate`: `assumption` required; ranges (`20–30%`), no invented precision (> 2 significant figures). Cost estimates cite the config they rest on in `source` |
| `migration` | ordered; `effort` S · M · L; `risk` Low · Medium · High; `rollback` required; steps fixing a High problem first, then quick wins (S + Low), unless `needs: [k]` (an earlier step) or `wait: "why"` |

Ids `A, B…` (diagrams), `5.1a` (traces) and step ids are added by the build. Problems sort High → Low; problem and change ids link both ways.

## Sections (fixed, always in this order)
1 Summary · 2 Current architecture · 3 Problems · 4 Proposed architecture (keep/move/later · target diagram · components + Stays · Main flows 4.k · Data model · Configuration · Security and access · Deploy and environments · Operations · Tests · Changes with Pick and Alternatives · Options) · 5 Workflows: current vs proposed · 6 Impact (one table, grouped by change; sources as basename:line, breaking after `_` and `.`, full path on hover) · 7 Migration · 8 Open questions and assumptions.
- Diagrams: ~10 boxes in 3 lanes leave little room for edge labels (`no room for arrow`): spread boxes over more columns, keep ≤ 3 edge labels, drop labels first. A box text cut with … → WARN: shorten `label`/`sub`.

## Checks
**ERROR** (no output): unknown `verdict`, `area`, `sev`, `dim`, `kind`, `effort`, `risk`, case, `decision`, `technical` section or block · move without `to`/`change` · `tool` without name/why, not 2–3 alternatives (on a change or a moves row), pick listed as an alternative, alternatives without a tool, a tool switch without `signal` · `components` row not 3 cells · `TODO` in any text · problem without evidence, evidence without a line, path not in the repo, absolute, `..`, `\`, lines past the file end, secret file with lines · change fixing no problem or an unknown one · change without an impact row · unknown change id in impact, workflows (`changes`, `needs`), migration or `top` · measured without `source`/`fact`, `fact` not in `facts.json`, estimate without `assumption` · options not 2–3 or not exactly one chosen, option without gains/costs · proposal diagram without a `new`/`changed` box · diagram without title, or one the renderer cannot lay out · ipo without input/steps/output, step without do/out, no trace, `at` count ≠ steps · migration without step/rollback/changes, `needs` not an earlier step · empty changes or migration · named review missing · secret literal or absolute path in any string · missing output folder.
**WARN**: moves empty · a moves row without alternatives (unless a move whose change has a `tool`) · `later` without `until` · a `move` row whose change has no `tool` · ≥ 3 `free_in` one tool with no move row (or later + `until`) to it · a tied text naming an alternative instead of the pick · "unchecked" / "not verified" / "if its … is" in a later row, option or question · a smaller option not chosen without `why_not` · a tool moves without a `Tests` section · no `typical` workflow · every trace synthetic while the inventory lists tests · option without `size` · every component moves without `redesign` · `redesign` with fewer than half moving · tool change with no `move` row · unknown `pattern` · a `technical` section missing · proposed strip without a `why` · measured number not in its cited lines · a duration marked measured without a number · High fix after a step fixing none (no `needs`/`wait`) · unticked checklist items · box text cut · word caps (any text ≤ 40 words, leads ≤ 2 sentences, strip `do` ≤ 8, strip and trace values ≤ 12) · filler words (robust, seamless, leverage, very, simply, …) · chat voice (`you` · `your` · `the user` · `Claude` · `as discussed` · `as agreed` · `as requested` · `per request` · `our conversation` · `confirm with` · `we could not check`) → write as the architect, open points as facts ("not yet tested in production") · the same sentence (≥ 6 words) twice · `N <fact>` in text ≠ `facts.json` · High problem without a change or `accept` · `keep` with a High problem or an L step · `redesign` without a High problem · L0 > 7 boxes or with lanes · diagram < 3 boxes · lane > 12 characters · > 7 steps · > 1 trace per strip · placeholder trace words · workflows not 2–3, title without `→`, no `changes` · invented precision · cost estimate without `source` · quick win after a slower step without `needs` · change in no migration step · empty runtime, hotspots, problems or stays · review in `reviews/` not named · subtitle form · no `inventory.json` next to the spec · graph commit ≠ HEAD · inventory older than the graph.
**note**: no repo files under the cwd (example built in an empty folder) → path, line, fact and graph checks skipped · docs-v2 missing.
**Added by the build:** stamp (date · repo commit `+dirty` · graph commit · review), `<meta name="repo-commit">` (for `--changed`), generator `darshan-singh-meel-architecture <version>`, the `.generated-by-darshan-singh-meel-docs` marker next to the HTML (repo builds only).
